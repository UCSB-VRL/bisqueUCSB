/*******************************************************************************

BQ::WebAccessDialog - download dialog in a form of a mini web browser 

Author: Dima Fedorov Levit <dimin@dimin.net> <http://www.dimin.net/>
        Center for Bio-image Informatics, UCSB

History:
2008-01-01 17:02 - First creation

ver: 2

*******************************************************************************/

#include <QtCore>
#include <QtGui>
#include <QtXml>
#include <QtNetwork>
#include <QtNetwork/QSslSocket>

#include <QtNetwork/QNetworkAccessManager>
#include <QtNetwork/QNetworkRequest>
#include <QtNetwork/QAuthenticator>
#include <QtNetwork/QNetworkDiskCache>
#include <QtNetwork/QNetworkProxy>
#include <QtNetwork/QNetworkRequest>
#include <QtNetwork/QNetworkReply>
#include <QtNetwork/QSslError>

#define BQ_ORGANIZATION    "UCSB"
#define BQ_APPLICATION     "Bisque"
#define BQ_CONFIG_FILE     "Bisque.ini"
#define BQ_VERSION         "0.0.2"

#include "bisqueWebAccess.h"
#include "bisque_api.h"

//---------------------------------------------------------------------------
// BQ::WebAccessDialog
//---------------------------------------------------------------------------

BQ::WebAccessDialog::WebAccessDialog() {

  setObjectName( "BisqueAccess" );
  ui.setupUi(this);
  file_path = QDir::currentPath();

  webView = new BQ::WebView(ui.groupBox);
  webView->setObjectName(QString::fromUtf8("webView"));
  ui.verticalLayout->addWidget(webView);
  webView->settings()->setAttribute(QWebSettings::JavascriptCanOpenWindows, true);
  webView->page()->setLinkDelegationPolicy( QWebPage::DelegateAllLinks );
  webView->page()->settings()->setAttribute(QWebSettings::JavascriptCanOpenWindows, true);

  QSettings conf( QSettings::IniFormat, QSettings::UserScope, BQ_ORGANIZATION, BQ_APPLICATION );
  ui.urlEdit->setText( conf.value( "url", "dough.ece.ucsb.edu" ).toString() );
  ui.userEdit->setText( conf.value( "user", "" ).toString() );
  ui.passwordEdit->setText( conf.value( "passwd", "" ).toString() );

  ui.autoLoadCheck->setChecked( conf.value( "AutoLoad", false ).toBool() );

  connect(webView, SIGNAL(loadProgress(int)), this, SLOT(onWebReadProgress(int)));
  connect(webView, SIGNAL(urlChanged ( const QUrl &)), this, SLOT(onUrlChanged ( const QUrl &)));
  connect(webView->page(), SIGNAL(linkClicked ( const QUrl &)), this, SLOT(onLinkClicked ( const QUrl &)));
  connect(ui.backButton, SIGNAL(clicked(bool)), webView, SLOT(back()));

  connect(ui.searchButton, SIGNAL(clicked(bool)), this, SLOT(onSearch()));

  connect(&bqAccess, SIGNAL(dataReadProgress(int,int)), this, SLOT(onHttpReadProgress(int,int)));
  connect(ui.cancelButton, SIGNAL(clicked(bool)), &bqAccess, SLOT(abort()));

  connect(ui.buttonBox->button(QDialogButtonBox::Close), SIGNAL(clicked(bool)), this, SLOT(onReject()));
  connect(ui.buttonBox->button(QDialogButtonBox::Open), SIGNAL(clicked(bool)), this, SLOT(onAccept()));
  connect(ui.pathLabel, SIGNAL(linkActivated(const QString &)), this, SLOT(onPathLabelLinkActivated( const QString &)));

#ifndef QT_NO_OPENSSL
    if (!QSslSocket::supportsSsl()) {
      QMessageBox::information(0, "Bisque Browser",
		"This system does not support OpenSSL. SSL websites will not be available.");
    }
#endif
  webView->page()->setNetworkAccessManager( &netman );
}

BQ::WebAccessDialog::~WebAccessDialog() {
  bqAccess.abort();
  QSettings conf( QSettings::IniFormat, QSettings::UserScope, BQ_ORGANIZATION, BQ_APPLICATION );  
  conf.setValue( "AutoLoad", ui.autoLoadCheck->isChecked() );
}

void BQ::WebAccessDialog::onReject() {
  bqAccess.abort();
  reject();
}

void BQ::WebAccessDialog::onAccept() {
  bqAccess.abort();
  onDownload();
  accept();
}

void BQ::WebAccessDialog::startProcess() {
  QApplication::setOverrideCursor(QCursor(Qt::WaitCursor));
  QApplication::processEvents();
}

void BQ::WebAccessDialog::inProcess( int done, int total, const QString &text ) {
  if (done!=total && time_progress.elapsed()<400 ) return;
  ui.progressBar->setMaximum( total );
  ui.progressBar->setValue( done );
  time_progress.start();
  if (!text.isEmpty()) ui.progressLabel->setText(text);
}

void BQ::WebAccessDialog::finishProcess() {
  QApplication::restoreOverrideCursor();
  QApplication::processEvents();
  ui.progressBar->setValue( 0 );
}

void BQ::WebAccessDialog::showErrors() {
  QString str;
  //ui.statusLabel->setText( str );
  ui.progressLabel->setText( str );
  /*
  int error = bqAccess.getHttp()->error();
  if (error > 0)
    ui.progressLabel->setText( bqAccess.getHttp()->errorString() );
  else {
    QHttpResponseHeader h = bqAccess.getHttp()->lastResponse();
    if ( h.statusCode() != 200 ) {
      str.sprintf("Status code: %d", h.statusCode() ); 
      ui.progressLabel->setText( str );
    }
  }
  */
}

void BQ::WebAccessDialog::showRequest( const QString &v ) {
  ui.progressLabel->setText( v );
}

void BQ::WebAccessDialog::onSearch() {
  QUrl url( ui.urlEdit->text() );
  if (ui.urlEdit->text().indexOf("://") == -1)
    url = QUrl( QString("http://")+ui.urlEdit->text() );

  QString user_name(ui.userEdit->text());
  QString password(ui.passwordEdit->text());

  QSettings conf( QSettings::IniFormat, QSettings::UserScope, BQ_ORGANIZATION, BQ_APPLICATION );
  conf.setValue( "url", url.toString() );
  conf.setValue( "user", user_name );
  conf.setValue( "passwd", password );

  bqAccess.setHost ( url  );
  bqAccess.setUserName ( user_name );
  bqAccess.setPassword ( password );
  
  // login hack
  url.setPath("/auth_service/login_handler");
  url.addQueryItem("login", user_name);
  url.addQueryItem("password", password);
  //url.addQueryItem("came_from", "/");

  // set request parameters - user name and password
  //QNetworkRequest request;
  //request.setUrl( url );
  //request.setRawHeader( "User-Agent", "Bisque WebKit 1.0" );

  //QString authorization = ui.userEdit->text() + ":" + ui.passwordEdit->text();
  //authorization = "Basic " + authorization.toLatin1().toBase64();
  //request.setRawHeader( "Authorization", authorization.toLatin1() );

  // Load
  qDebug( url.toString().toLatin1().constData() );
  showRequest( url.toString() );
  webView->load( url );
  //webView->load( request );
}

void BQ::WebAccessDialog::onWebReadProgress ( int done ) {
  inProcess( done, 100, webView->url().toString() );
}

void BQ::WebAccessDialog::onHttpReadProgress ( int done, int total ) {
  QString s;
  QStringList state_strings;
  state_strings << "Unconnected" << "HostLookup" << "Connecting" << "Sending" << "Reading" << "Connected" << "Closing";
  //QHttp *http = bqAccess.getHttp();
  //s = state_strings[http->state()] + " " + bqAccess.currentUrl().toString();
  //inProcess( done, total, s );
}

void BQ::WebAccessDialog::onUrlChanged ( const QUrl & url ) {
  QString u = url.toString();
  qDebug( url.toString().toLatin1().constData() );

  if ( ui.autoLoadCheck->isChecked() && u.indexOf("?resource=") != -1) {
    u.remove ( QRegExp("^.*\\?resource=") );
    doDownload( QUrl( u ) );
    accept();
  }
}

void BQ::WebAccessDialog::onLinkClicked ( const QUrl & url ) {
  webView->load( url );
}

void BQ::WebAccessDialog::onDownload( ) {
  QUrl url = webView->url();
  QString u = url.toString();

  if (u.indexOf("?resource=") != -1) {
    u.remove ( QRegExp("^.*\\?resource=") );
    doDownload( QUrl( u ) );
    accept();
  }    
}

void BQ::WebAccessDialog::doDownload( const QUrl & u ) {
  QUrl url(u);
  qDebug( url.toString().toLatin1().constData() );
  startProcess();

  BQ::Image image( url, ui.userEdit->text(), ui.passwordEdit->text() ); // dima: here use Factory
  //BQ::Image image = * (BQ::Image*) BQ::Factory::fetch( url, ui.userEdit->text(), ui.passwordEdit->text() ); 
  QString fileName = file_path + "/" + image.getAttribute("name");
  if (image.fetch( fileName ) == 0)
      image_file_name = fileName;

  fileName = fileName + ".gox";
  url.setPath(url.path()+"/gobject");
  BQ::Node gobs( url, ui.userEdit->text(), ui.passwordEdit->text() ); // dima: here use Factory
  //BQ::Node gobs = * BQ::Factory::fetch( url, ui.userEdit->text(), ui.passwordEdit->text() ); 
  if (gobs.fetch( fileName ) == 0)
      gob_file_name = fileName;

  showErrors();
  finishProcess();
}

void BQ::WebAccessDialog::onPathLabelLinkActivated ( const QString & ) {
  
  QString dir = QFileDialog::getExistingDirectory( this, tr("Open Directory"), file_path );
  if (!dir.isEmpty())
    setPath( dir );
}

//---------------------------------------------------------------------------
// BQ::WebView required for the webview to access SSL secure sites
//---------------------------------------------------------------------------

BQ::WebView::WebView(QWidget *parent) : QWebView(parent) {
  this->setPage( new BQ::WebPage() );
}

//QWebView* BQ::WebView::createWindow ( QWebPage::WebWindowType /*type*/ ) {
//  //return this;
//  return 0;
//}

BQ::WebPage::WebPage(QWidget *parent) : QWebPage(parent) {
}

QWebPage* BQ::WebPage::createWindow ( QWebPage::WebWindowType /*type*/ ) {
  return this;
}



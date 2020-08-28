
#include <QtCore>
#include <QtGui>
#include <QtNetwork>
#include <QtXml>

#define BQ_ORGANIZATION    "UCSB"
#define BQ_APPLICATION     "Bisquik"
#define BQ_CONFIG_FILE     "bisquik.ini"
#define BQ_VERSION         "0.0.1"

#include "bisquikWebAccess.h"

//---------------------------------------------------------------------------
// BQWebAccessDialog
//---------------------------------------------------------------------------

BQWebAccessDialog::BQWebAccessDialog() {

  setObjectName( "BisquikAccess" );
  ui.setupUi(this);
  file_path = QDir::currentPath();

  QSettings conf( QSettings::IniFormat, QSettings::UserScope, BQ_ORGANIZATION, BQ_APPLICATION );
  ui.urlEdit->setText( conf.value( "url", "dough.ece.ucsb.edu" ).toString() );
  ui.userEdit->setText( conf.value( "user", "" ).toString() );
  ui.passwordEdit->setText( conf.value( "passwd", "" ).toString() );

  ui.autoLoadCheck->setChecked( conf.value( "AutoLoad", false ).toBool() );

  connect(ui.webView, SIGNAL(loadProgress(int)), this, SLOT(onWebReadProgress(int)));
  connect(ui.webView, SIGNAL(urlChanged ( const QUrl &)), this, SLOT(onUrlChanged ( const QUrl &)));
  connect(ui.backButton, SIGNAL(clicked(bool)), ui.webView, SLOT(back()));

  connect(ui.searchButton, SIGNAL(clicked(bool)), this, SLOT(onSearch()));

  connect(&bqAccess, SIGNAL(dataReadProgress(int,int)), this, SLOT(onHttpReadProgress(int,int)));
  connect(ui.cancelButton, SIGNAL(clicked(bool)), &bqAccess, SLOT(abort()));

  connect(ui.buttonBox->button(QDialogButtonBox::Close), SIGNAL(clicked(bool)), this, SLOT(onReject()));
  connect(ui.buttonBox->button(QDialogButtonBox::Open), SIGNAL(clicked(bool)), this, SLOT(onAccept()));
  connect(ui.pathLabel, SIGNAL(linkActivated(const QString &)), this, SLOT(onPathLabelLinkActivated( const QString &)));
}

BQWebAccessDialog::~BQWebAccessDialog() {
  QSettings conf( QSettings::IniFormat, QSettings::UserScope, BQ_ORGANIZATION, BQ_APPLICATION );  
  conf.setValue( "AutoLoad", ui.autoLoadCheck->isChecked() );
}

void BQWebAccessDialog::onReject() {
  bqAccess.abort();
  reject();
}

void BQWebAccessDialog::onAccept() {
  bqAccess.abort();
  onDownload();
  accept();
}

void BQWebAccessDialog::startProcess() {
  QApplication::setOverrideCursor(QCursor(Qt::WaitCursor));
  QApplication::processEvents();
}

void BQWebAccessDialog::inProcess( int done, int total, const QString &text ) {
  if (done!=total && time_progress.elapsed()<400 ) return;
  ui.progressBar->setMaximum( total );
  ui.progressBar->setValue( done );
  time_progress.start();
  if (!text.isEmpty()) ui.progressLabel->setText(text);
}

void BQWebAccessDialog::finishProcess() {
  QApplication::restoreOverrideCursor();
  QApplication::processEvents();
  ui.progressBar->setValue( 0 );
}

void BQWebAccessDialog::showErrors() {
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

void BQWebAccessDialog::showRequest( const QString &v ) {
  ui.progressLabel->setText( v );
}

void BQWebAccessDialog::onSearch() {
  QUrl url( ui.urlEdit->text() );
  if (ui.urlEdit->text().indexOf("://") == -1)
    url = QUrl( QString("http://")+ui.urlEdit->text() );

  QSettings conf( QSettings::IniFormat, QSettings::UserScope, BQ_ORGANIZATION, BQ_APPLICATION );
  conf.setValue( "url", url.toString() );
  conf.setValue( "user", ui.userEdit->text() );
  conf.setValue( "passwd", ui.passwordEdit->text() );

  bqAccess.setHost ( url  );
  bqAccess.setUserName ( ui.userEdit->text() );
  bqAccess.setPassword ( ui.passwordEdit->text() );

  url.setPath("/bisquik/browser");


  // set request parameters - user name and password
  QNetworkRequest request;
  request.setUrl( url );
  request.setRawHeader( "User-Agent", "BisqueBrowser 1.0" );

  QString authorization = ui.userEdit->text() + ":" + ui.passwordEdit->text();
  authorization = "Basic " + authorization.toLatin1().toBase64();
  request.setRawHeader( "Authorization", authorization.toLatin1() );

  // Load
  showRequest( ui.webView->url().toString() );
  //ui.webView->load( url );
  ui.webView->load( request );
}

void BQWebAccessDialog::onWebReadProgress ( int done ) {
  inProcess( done, 100, ui.webView->url().toString() );
}

void BQWebAccessDialog::onHttpReadProgress ( int done, int total ) {
  QString s;
  QStringList state_strings;
  state_strings << "Unconnected" << "HostLookup" << "Connecting" << "Sending" << "Reading" << "Connected" << "Closing";
  QHttp *http = bqAccess.getHttp();
  s = state_strings[http->state()] + " " + bqAccess.currentUrl().toString();
  inProcess( done, total, s );
}

void BQWebAccessDialog::onUrlChanged ( const QUrl & url ) {
  QString u = url.toString();
  
  if ( ui.autoLoadCheck->isChecked() && u.indexOf("?resource=") != -1) {
    u.remove ( QRegExp("^.*\\?resource=") );
    doDownload( QUrl( u ) );
    accept();
  }
}

void BQWebAccessDialog::onDownload( ) {
  QUrl url = ui.webView->url();
  QString u = url.toString();

  if (u.indexOf("?resource=") != -1) {
    u.remove ( QRegExp("^.*\\?resource=") );
    doDownload( QUrl( u ) );
    accept();
  }    
}

void BQWebAccessDialog::doDownload( const QUrl & url ) {

  startProcess();
  bqAccess.setUserName ( ui.userEdit->text() );
  bqAccess.setPassword ( ui.passwordEdit->text() );
  BQImageItem imageItem = bqAccess.getImage( url );

  QString fileName = bqAccess.getImageFileName( imageItem.src );
  fileName = file_path + "/" + fileName;
  if (bqAccess.getImageFile( imageItem.src, fileName ) == 0)
    image_file_name = fileName;

  fileName = fileName + ".gox";
  if (bqAccess.getImageGObjects( imageItem.uri, fileName ) == 0)
    gob_file_name = fileName;

  showErrors();
  finishProcess();
}

void BQWebAccessDialog::onPathLabelLinkActivated ( const QString & ) {
  
  QString dir = QFileDialog::getExistingDirectory( this, tr("Open Directory"), file_path );
  if (!dir.isEmpty())
    setPath( dir );
}


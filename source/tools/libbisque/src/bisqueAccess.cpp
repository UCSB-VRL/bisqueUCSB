
#include <QtCore>
#include <QtGui>
#include <QtNetwork>
#include <QtXml>

#define BQ_ORGANIZATION    "UCSB"
#define BQ_APPLICATION     "Bisque"
#define BQ_CONFIG_FILE     "Bisque.ini"
#define BQ_VERSION         "0.0.3"

#include "BisqueAccess.h"
#include "bisque_api.h"

#define BQ_SLEEP 10 // 200
#define BQ_PROGRESS_SLEEP 100

/*

//---------------------------------------------------------------------------
// BQAccessDialog
//---------------------------------------------------------------------------

BQ::AccessDialog::AccessDialog() {
  setObjectName( "BisqueAccess" );
  ui.setupUi(this);
  file_path = QDir::currentPath();
  currentRow = -1;

  ui.downloadButton->setVisible( false );

  QSettings conf( QSettings::IniFormat, QSettings::UserScope, BQ_ORGANIZATION, BQ_APPLICATION );
  ui.urlEdit->setText( conf.value( "url", "bisque.ece.ucsb.edu" ).toString() );
  ui.userEdit->setText( conf.value( "user", "" ).toString() );
  ui.passwordEdit->setText( conf.value( "passwd", "" ).toString() );

  connect(ui.searchButton, SIGNAL(clicked(bool)), this, SLOT(onSearch()));
  connect(ui.imagesListWidget, SIGNAL(itemActivated(QListWidgetItem*)), this, SLOT(onItemActivated(QListWidgetItem*)));
  connect(ui.imagesListWidget, SIGNAL(currentItemChanged(QListWidgetItem*,QListWidgetItem *)), this, SLOT(onItemActivated(QListWidgetItem*)));

  connect(&bqAccess, SIGNAL(dataReadProgress(int,int)), this, SLOT(onHttpReadProgress(int,int)));
  connect(ui.cancelButton, SIGNAL(clicked(bool)), &bqAccess, SLOT(abort()));

  connect(ui.downloadButton, SIGNAL(clicked(bool)), this, SLOT(onDownload()));
  connect(ui.buttonBox->button(QDialogButtonBox::Close), SIGNAL(clicked(bool)), this, SLOT(onReject()));
  connect(ui.buttonBox->button(QDialogButtonBox::Open), SIGNAL(clicked(bool)), this, SLOT(onAccept()));

  connect(ui.pathLabel, SIGNAL(linkActivated(const QString &)), this, SLOT(onPathLabelLinkActivated( const QString &)));
}

void BQ::AccessDialog::onReject() {
  bqAccess.abort();
  reject();
}

void BQ::AccessDialog::onAccept() {
  bqAccess.abort();
  onDownload();
  accept();
}

void BQ::AccessDialog::startProcess() {
  QApplication::setOverrideCursor(QCursor(Qt::WaitCursor));
  QApplication::processEvents();
}

void BQ::AccessDialog::inProcess( int done, int total, const QString &text ) {
  if (time_progress.elapsed() < BQ_PROGRESS_SLEEP ) return;
  ui.progressBar->setMaximum( total );
  ui.progressBar->setValue( done );
  time_progress.start();
  if (!text.isEmpty()) ui.progressLabel->setText(text);
}

void BQ::AccessDialog::finishProcess() {
  QApplication::restoreOverrideCursor();
  QApplication::processEvents();
  ui.progressBar->setValue( 0 );
}

void BQ::AccessDialog::showErrors() {
  QString str;
  ui.progressLabel->setText( str );
  int error = bqAccess.getError();
  if (error > 0) {
    //ui.progressLabel->setText( bqAccess.getHttp()->errorString() );
  } else {
    //QHttpResponseHeader h = bqAccess.getHttp()->lastResponse();
    //if ( h.statusCode() != 200 ) {
    //  str.sprintf("Status code: %d", h.statusCode() ); 
    //  ui.progressLabel->setText( str );
    //}
  }
}

void BQ::AccessDialog::showRequest( const QString &v ) {
  //ui.statusLabel->setText( v );
  ui.progressLabel->setText( v );
}

void BQ::AccessDialog::onSearch() {
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

  showRequest( bqAccess.host().toString() );
  ui.imagesListWidget->clear();
  startProcess();
  images = bqAccess.getImages( ui.searchEdit->text() );
  //url.setPath( "ds/images/" );
  ui.imagesListWidget->addItems ( images.toStringList( url ) ) ;
  showErrors();
  finishProcess();
}

void BQ::AccessDialog::onItemActivated ( QListWidgetItem * item ) {
  bqAccess.abort();

  int row = ui.imagesListWidget->row( item ); 
  if (row >= images.size()) return;
  currentRow = row;

  showRequest( images[row].src );
  startProcess();
  QString fileName = images[row].name;
  ui.fileNameLabel->setText( fileName );

  QPixmap image = bqAccess.getImageThumbnail( images[row].src );
  ui.imageLabel->setPixmap( image );

  if (ui.showTagsCheck->isChecked()) { // if load tags
    QHash<QString, QString> tags = bqAccess.getImageTags( images[row].uri );
    ui.TagsTableWidget->setColumnCount( 2 );
    ui.TagsTableWidget->setRowCount( tags.size() );
    QHash<QString, QString>::const_iterator it = tags.begin();
    for (int i=0; i<tags.size(); ++i) {
      QTableWidgetItem *ki = new QTableWidgetItem( it.key() );
      ui.TagsTableWidget->setItem ( i, 0, ki ); 
      ki = new QTableWidgetItem( it.value() );
      ui.TagsTableWidget->setItem ( i, 1, ki ); 
      ++it;
    }
    ui.TagsTableWidget->resizeColumnsToContents(); 
    ui.TagsTableWidget->resizeRowsToContents();
  } else 
    ui.TagsTableWidget->clear();
  showErrors();
  finishProcess();
}

void BQ::AccessDialog::onHttpReadProgress ( int done, int total ) {
  QString s;
  QStringList state_strings;
  state_strings << "Unconnected" << "HostLookup" << "Connecting" << "Sending" << "Reading" << "Connected" << "Closing";
  //QHttp *http = bqAccess.getHttp();
  //s = state_strings[http->state()] + " " + bqAccess.currentUrl().toString();
  //inProcess( done, total, s );
}

void BQ::AccessDialog::onDownload() {
  if (currentRow == -1) return;

  startProcess();
  QString fileName = images[currentRow].name;
  fileName = file_path + "/" + fileName;
  if (bqAccess.getImageFile( images[currentRow].src, fileName ) == 0)
    image_file_name = fileName;

  fileName = fileName + ".gox";
  if (bqAccess.getImageGObjects( images[currentRow].uri, fileName ) == 0)
    gob_file_name = fileName;

  showErrors();
  finishProcess();
  //accept();
}

void BQ::AccessDialog::onPathLabelLinkActivated ( const QString & ) {
  
  QString dir = QFileDialog::getExistingDirectory( this, tr("Open Directory"), file_path );
  if (!dir.isEmpty())
    setPath( dir );
}

*/

//---------------------------------------------------------------------------
// BQ::NetworkReply
//---------------------------------------------------------------------------

BQ::NetworkReply::NetworkReply( QNetworkReply *reply, QIODevice *iod ) {
    this->reply = reply;
    this->iod = iod;
    this->stopWatch.start();
    connect(this->reply, SIGNAL(error(QNetworkReply::NetworkError)), this, SLOT(onError(QNetworkReply::NetworkError)));
    connect(this->reply, SIGNAL(readyRead()), this, SLOT(onReadyRead()));
    connect(this->reply, SIGNAL(downloadProgress(qint64, qint64)), this, SLOT(onReadProgress (qint64, qint64)));
}

BQ::NetworkReply::~NetworkReply() {
    this->reply->deleteLater();
}

void BQ::NetworkReply::onReadProgress ( qint64 bytesReceived, qint64 bytesTotal ) {
    emit dataReadProgress ( bytesReceived, bytesTotal ); 
}

void BQ::NetworkReply::onReadyRead () {
    this->stopWatch.start();
    this->iod->write( this->reply->readAll() );
}

void BQ::NetworkReply::onError ( QNetworkReply::NetworkError ) {

}


//---------------------------------------------------------------------------
// BQ::AccessBase
//---------------------------------------------------------------------------

BQ::AccessBase::AccessBase() {
    this->init();
}

BQ::AccessBase::AccessBase(const QUrl &url, const QString &user, const QString &pass ) {
    this->init();
    this->user = user;
    this->pass = pass;
}

void BQ::AccessBase::init() {
    this->net = new BQ::NetworkAccessManager();
    stop_request = false;
    done_incremental = 0;
    //connect(net, SIGNAL(finished(QNetworkReply*)), this, SLOT(onReplyFinished(QNetworkReply*)));
}

QString ensureFrontBackslash( const QString &s ) {
  QString v = s;
  if ( v[0] != QChar('/') ) v.insert(0, QChar('/'));
  return v;
}

int BQ::AccessBase::request( const QUrl &url, QIODevice *iod, int timeout ) {
    this->net->setUserName(this->user);
    this->net->setPassword(this->pass);
    progress.start();  
    done_incremental=0;  
    current_url = url;
    emit dataReadProgress(0, 100);
    qDebug( url.toString().toLatin1().constData() );

    QNetworkRequest request(url);
    QString authorization = user + ":" + pass;
    authorization = "Basic " + authorization.toLatin1().toBase64();
    request.setRawHeader("Authorization", authorization.toLatin1() );
    request.setRawHeader("User-Agent",    "Bisque C++ API 2.0");
    request.setRawHeader("Keep-Alive",    "300");
    request.setRawHeader("Connection",    "keep-alive");
    request.setRawHeader("Accept",        "text/xml,application/xml");

    // ignore all peer SSL verification
    #ifndef QT_NO_OPENSSL
    QSslConfiguration sslconf = request.sslConfiguration();
    sslconf.setPeerVerifyMode(QSslSocket::VerifyNone);
    request.setSslConfiguration(sslconf);
    #endif

    stop_request = false;
    QNetworkReply *r = net->get(request);
    BQ::NetworkReply *reply = new BQ::NetworkReply( r, iod );
    connect(reply, SIGNAL(dataReadProgress(qint64, qint64)), this, SLOT(onReadProgress (qint64, qint64)));

    while (reply && reply->isRunning() && !stop_request ) {
        if (reply->timeElapsed() > timeout) { reply->abort(); break; }
        QApplication::processEvents();
        QSleepyThread::doMSleep( BQ_SLEEP );
    }
    emit dataReadProgress(100, 100);
    lasterror = reply->getError();
    delete reply;
    return lasterror;
}

void BQ::AccessBase::onReadProgress ( qint64 done, qint64 total ) {
  if (progress.elapsed() < BQ_PROGRESS_SLEEP ) return;
  progress.start();

  if (total>0) {
    emit dataReadProgress ( done, total ); 
    return;
  }

  // in case the size of the response is not specified, use simple incremental updates
  done_incremental += 1;
  emit dataReadProgress ( done_incremental, 255 ); 
}

void BQ::AccessBase::onReplyFinished (QNetworkReply *reply) {
}

QByteArray BQ::AccessBase::request( const QUrl &url, int timeout ) {

  QBuffer buffer;
  buffer.open(QBuffer::ReadWrite);

  if ( request(url, &buffer, timeout) == 0 )
    return buffer.buffer();  
  else
    return buffer.buffer();  
}

void BQ::AccessBase::setHost( const QUrl &v ) { 
  hostUrl = v; 
  if (hostUrl.scheme().isEmpty()) 
    hostUrl.setScheme("http");
}


//---------------------------------------------------------------------------
// BQAccess
//---------------------------------------------------------------------------
/*
BQ::Access::Access() : BQ::AccessBase() {
}

BQ::ImageList BQ::Access::getImages( const QString &query ) {
  BQ::ImageList images;
  QUrl url( hostUrl );
  url.setPath( "/data_service/image?tag_query="+QUrl::toPercentEncoding( query ) );
  QString xml = request( url, BQ_TIMEOUT );

  QDomDocument doc("mydocument");
  if ( doc.setContent(xml) ) {
    QDomElement root = doc.documentElement();
    QDomElement node = root.firstChildElement("image");
    while ( !node.isNull() ) {
      images << BQ::ImageItem(node);
      node = node.nextSiblingElement("image");
    } // while
  }
  return images;
}

QString BQ::Access::getObject( const QUrl &url ) {
  return request( url, BQ_TIMEOUT );
}

int BQ::Access::getObject( const QUrl &url, const QString &fileName ) {
  QFile file( fileName );
  file.open( QIODevice::WriteOnly );
  int r = request( url, &file, BQ_TIMEOUT );
  file.flush();
  file.close();
  return r;
}

BQ::ImageItem BQ::Access::getImage( const QUrl &url ) {
  BQ::ImageItem image;
  QString xml = request( url, BQ_TIMEOUT );
  qDebug(xml.toLatin1().constData());

  QDomDocument doc("mydocument");
  if ( doc.setContent(xml) ) {
    QDomElement node = doc.documentElement();
    if (!node.isNull() && node.tagName() != "image")
      node = node.firstChildElement("image");
    if ( !node.isNull() ) {
      image = BQ::ImageItem(node);
    } // while
  }
  return image;
}

QHash<QString, QString> BQ::Access::getImageTags( const QUrl &url ) {
  QHash<QString, QString> tags;
  QUrl imgurl( url );
  QString path = url.path() + "/tag";
  imgurl.setPath( path );

  QString xml = request( imgurl, BQ_TIMEOUT );
  QDomDocument doc("mydocument");
  if ( doc.setContent(xml) ) {
    QDomElement root = doc.documentElement();
    QDomElement node = root.firstChildElement("tag");
    while ( !node.isNull() ) {
      QString name, value;
      if (node.hasAttribute("name")) name = node.attribute("name");
      if (node.hasAttribute("value")) value = node.attribute("value");
      tags.insert( name, value );
      node = node.nextSiblingElement("tag");
    } // while
  }
  return tags;
}

QString BQ::Access::getImageGObjects( const QUrl &url ) {

  QUrl imgurl( url );
  QString path = url.path() + "/gobject?view=deep";
  imgurl.setPath( path );
  return request( imgurl, BQ_TIMEOUT );
}

int BQ::Access::getImageGObjects( const QUrl &url, const QString &fileName ) {
  QUrl imgurl( url );
  QString path = url.path() + "/gobject";
  imgurl.setPath( path );
  imgurl.addQueryItem( "view", "deep" );
  imgurl.addQueryItem( "wpublic", "1" );
  QFile file( fileName );
  return request( imgurl, &file, BQ_TIMEOUT );
}

QPixmap BQ::Access::getImageThumbnail( const QUrl &url ) {
  QPixmap image;
  QUrl imgurl( url );
  QList<QByteArray> fl= QImageReader::supportedImageFormats();
  
  QString path = url.path() + "?thumbnail=200,200,BC";
  if (fl.indexOf("JPEG")==-1) {
    // If Qt does not have jpeg reader
    path = url.path() + "?remap=display&slice=,,0,0&resize=200,200,BC,AR&format=bmp";
  }

  imgurl.setPath( path );

  QBuffer buffer;
  buffer.open(QBuffer::ReadWrite);
  if (request( imgurl, &buffer, BQ_TIMEOUT ) == 0)
    image.loadFromData( buffer.buffer() );

  return image;
}

int BQ::Access::getImageFile( const QUrl &url, const QString &fileName ) {
  //content-disposition: attachment; filename="161pkcvampz1Live2-17-2004_11-57-21_AM.tif"
  QFile file( fileName );
  file.open( QIODevice::WriteOnly );
  int r = request( url, &file, BQ_TIMEOUT );
  file.flush();
  file.close();
  return r;
}

QString BQ::Access::getGObjects( const QUrl &url ) {
  QUrl u( url );
  u.addQueryItem( "view", "deep" );
  return getObject( u );
}

int BQ::Access::getGObjects( const QUrl &url, const QString &fileName ) {
  QUrl u( url );
  u.addQueryItem( "view", "deep" );
  QString str2 = u.toString();
  return getObject( u, fileName );
}


//---------------------------------------------------------------------------
// BQ::ImageItem
//---------------------------------------------------------------------------

BQ::ImageItem::ImageItem( const QDomElement &node ) {
  fromXML( node );
}

void BQ::ImageItem::fromXML( const QDomElement &node ) {
  perm=0; t=0; y=0; x=0; z=0; ch=0;

  if (node.hasAttribute("uri"))  uri  = node.attribute("uri");
  if (node.hasAttribute("src"))  src  = node.attribute("src");
  if (node.hasAttribute("name")) name = node.attribute("name");
  if (this->name.isEmpty()) {
    this->name = "bisque_image_" + QUrl::toPercentEncoding ( this->uri, QByteArray(), "/" );
  }

  if (node.hasAttribute("perm")) perm = node.attribute("perm").toInt();
  if (node.hasAttribute("x")) x = node.attribute("x").toInt();
  if (node.hasAttribute("y")) y = node.attribute("y").toInt();
  if (node.hasAttribute("z")) z = node.attribute("z").toInt();
  if (node.hasAttribute("t")) t = node.attribute("t").toInt();
  if (node.hasAttribute("ch")) ch = node.attribute("ch").toInt();
  if (node.hasAttribute("ts")) ts = QDateTime::fromString( node.attribute("ts"), "yyyy-MM-dd HH:mm:ss" );

  if (node.hasAttribute("resource_uniq")) {
      QUrl u(this->uri);
      u.setPath( QString("/image_service/") + node.attribute("resource_uniq") );
      //u.setEncodedQuery("");
      this->src = u.toString();
  }
}

QString BQ::ImageItem::toString(const QUrl &u) const {
  QString text;
  text.sprintf(" ( %dx%dx%dx%dx%d )", x, y, z, t, ch );
  QString url = uri;
  text = url.remove( 0, u.toString().size() ) + text;
  return text;
}

//---------------------------------------------------------------------------
// BQ::ImageList
//---------------------------------------------------------------------------

QStringList BQ::ImageList::toStringList( const QUrl &u ) const {
  QStringList ls;
  for (int i=0; i<this->size(); ++i)
    ls << (*this)[i].toString(u);
  return ls;
}
*/

//---------------------------------------------------------------------------
// BQ::Url
//---------------------------------------------------------------------------

//"bioview3d://resource/?user=name&pass=pass&url=http://vidi.ece.ucsb.edu:8080/ds/images/1073"

BQ::Url::Url( const QString &in_url ) {
  u = QUrl( in_url );
}

QString BQ::Url::argument( const QString &item ) const {
  return u.queryItemValue( item );
}

//---------------------------------------------------------------------------
// BQ::AccessWrapper
//---------------------------------------------------------------------------

BQ::AccessWrapper::AccessWrapper() {

  file_path = QDir::currentPath();
  connect(&bqAccess, SIGNAL(dataReadProgress(int,int)), this, SLOT(onHttpReadProgress(int,int)));
}

void BQ::AccessWrapper::onHttpReadProgress ( int done, int total ) {
  QString s;
  QStringList state_strings;
  state_strings << "Unconnected" << "HostLookup" << "Connecting" << "Sending" << "Reading" << "Connected" << "Closing";
}

bool BQ::AccessWrapper::doDownload( const QUrl &url, const QUrl &gobjects ) {
  emit startProcess();
  qDebug( url.toString().toLatin1().constData() );
  startProcess();

  //BQ::Image image( url, bqAccess.userName(), bqAccess.password() ); // dima: here use Factory
  BQ::Image image = * (BQ::Image*) BQ::Factory::fetch( url, bqAccess.userName(), bqAccess.password() ); 
  QString fileName = file_path + "/" + image.getAttribute("name");
  if (image.fetch( fileName ) == 0)
      image_file_name = fileName;

  fileName = fileName + ".gox";
  BQ::Node gobs( gobjects, bqAccess.userName(), bqAccess.password() ); // dima: here use Factory
  //BQ::Node gobs = * BQ::Factory::fetch( url, bqAccess.userName(), bqAccess.password() ); 
  if (gobs.fetch( fileName ) == 0)
      gob_file_name = fileName;

  emit finishProcess();
  return true;
}


/***************************************************************************/
// BQ::NetworkAccessManager required for the webview to access SSL secure sites
/***************************************************************************/

BQ::NetworkAccessManager::NetworkAccessManager(QObject *parent)
    : QNetworkAccessManager(parent)
{
#ifndef QT_NO_OPENSSL
    connect(this, SIGNAL(sslErrors(QNetworkReply*, const QList<QSslError>&)),
            SLOT(sslErrors(QNetworkReply*, const QList<QSslError>&)));
#endif
    connect(this, SIGNAL(authenticationRequired(QNetworkReply*, QAuthenticator*)),
            SLOT(provideAuthentication(QNetworkReply*, QAuthenticator*)));
}

void BQ::NetworkAccessManager::sslErrors(QNetworkReply *reply, const QList<QSslError> &error) {
#ifndef QT_NO_OPENSSL
	// check if SSL certificate has been trusted already
	QString replyHost = reply->url().host() + ":" + reply->url().port();
	if(! sslTrustedHostList.contains(replyHost)) {
		QStringList errorStrings;
		for (int i = 0; i < error.count(); ++i)
			errorStrings += error.at(i).errorString();
		QString errors = errorStrings.join(QLatin1String("\n"));
		int ret = QMessageBox::warning(0, QCoreApplication::applicationName(),
				tr("SSL Errors:\n\n%1\n\n%2\n\n"
						"Do you want to ignore these errors for this host?").arg(reply->url().toString()).arg(errors),
						QMessageBox::Yes | QMessageBox::No,
						QMessageBox::No);
		if (ret == QMessageBox::Yes) {
			reply->ignoreSslErrors();
			sslTrustedHostList.append(replyHost);
		}
	}
#endif
}

void BQ::NetworkAccessManager::provideAuthentication(QNetworkReply *reply, QAuthenticator *auth) {
    if (!this->user.isEmpty() && !this->pass.isEmpty()) {
        auth->setUser(this->user);
        auth->setPassword(this->pass);
    }
}


#include <QtCore>
#include <QtGui>
#include <QtNetwork>
#include <QtXml>

#define BQ_ORGANIZATION    "UCSB"
#define BQ_APPLICATION     "Bisquik"
#define BQ_CONFIG_FILE     "bisquik.ini"
#define BQ_VERSION         "0.0.2"

#include "bisquikAccess.h"

#define BQ_TIMEOUT 10000000
#define BQ_SLEEP 50 // 200


//---------------------------------------------------------------------------
// BQAccessDialog
//---------------------------------------------------------------------------

BQAccessDialog::BQAccessDialog() {

  setObjectName( "BisquikAccess" );
  ui.setupUi(this);
  file_path = QDir::currentPath();
  currentRow = -1;

  ui.downloadButton->setVisible( false );

  QSettings conf( QSettings::IniFormat, QSettings::UserScope, BQ_ORGANIZATION, BQ_APPLICATION );
  ui.urlEdit->setText( conf.value( "url", "dough.ece.ucsb.edu" ).toString() );
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

void BQAccessDialog::onReject() {
  bqAccess.abort();
  reject();
}

void BQAccessDialog::onAccept() {
  bqAccess.abort();
  onDownload();
  accept();
}

void BQAccessDialog::startProcess() {
  QApplication::setOverrideCursor(QCursor(Qt::WaitCursor));
  QApplication::processEvents();
}

void BQAccessDialog::inProcess( int done, int total, const QString &text ) {
  if (time_progress.elapsed() < 400 ) return;
  ui.progressBar->setMaximum( total );
  ui.progressBar->setValue( done );
  time_progress.start();
  if (!text.isEmpty()) ui.progressLabel->setText(text);
}

void BQAccessDialog::finishProcess() {
  QApplication::restoreOverrideCursor();
  QApplication::processEvents();
  ui.progressBar->setValue( 0 );
}

void BQAccessDialog::showErrors() {
  QString str;
  //ui.statusLabel->setText( str );
  ui.progressLabel->setText( str );
  int error = bqAccess.getHttp()->error();
  if (error > 0)
    //ui.statusLabel->setText( bqAccess.getHttp()->errorString() );
    ui.progressLabel->setText( bqAccess.getHttp()->errorString() );
  else {
    QHttpResponseHeader h = bqAccess.getHttp()->lastResponse();
    if ( h.statusCode() != 200 ) {
      str.sprintf("Status code: %d", h.statusCode() ); 
      //ui.statusLabel->setText( str );
      ui.progressLabel->setText( str );
    }
  }
}

void BQAccessDialog::showRequest( const QString &v ) {
  //ui.statusLabel->setText( v );
  ui.progressLabel->setText( v );
}

void BQAccessDialog::onSearch() {
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

void BQAccessDialog::onItemActivated ( QListWidgetItem * item ) {
  bqAccess.abort();

  int row = ui.imagesListWidget->row( item ); 
  if (row >= images.size()) return;
  currentRow = row;

  showRequest( images[row].src );
  startProcess();
  QString fileName = bqAccess.getImageFileName( images[row].src );
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

void BQAccessDialog::onHttpReadProgress ( int done, int total ) {
  QString s;
  QStringList state_strings;
  state_strings << "Unconnected" << "HostLookup" << "Connecting" << "Sending" << "Reading" << "Connected" << "Closing";
  QHttp *http = bqAccess.getHttp();
  s = state_strings[http->state()] + " " + bqAccess.currentUrl().toString();
  inProcess( done, total, s );
}

void BQAccessDialog::onDownload() {
  if (currentRow == -1) return;

  startProcess();
  QString fileName = bqAccess.getImageFileName( images[currentRow].src );
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

void BQAccessDialog::onPathLabelLinkActivated ( const QString & ) {
  
  QString dir = QFileDialog::getExistingDirectory( this, tr("Open Directory"), file_path );
  if (!dir.isEmpty())
    setPath( dir );
}

//---------------------------------------------------------------------------
// BQAccess
//---------------------------------------------------------------------------

BQAccessBase::BQAccessBase() {
  stop_request = false;
  connect(&http, SIGNAL(dataReadProgress(int,int)), this, SLOT(onHttpReadProgress(int,int)));
  connect(&http, SIGNAL(requestFinished(int, bool)), this, SLOT(onRequestFinished(int, bool)));
}

QString ensureFrontBackslash( const QString &s ) {
  QString v = s;
  if ( v[0] != QChar('/') ) v.insert(0, QChar('/'));
  return v;
}

int BQAccessBase::request( const QUrl &url, QIODevice *iod, int timeout ) {
  current_url = url;
  emit dataReadProgress(0, 100);

  if (url.port()>0) 
    http.setHost( url.host(), QHttp::ConnectionModeHttp, url.port() );
  else
    http.setHost( url.host(), QHttp::ConnectionModeHttp );
  http.setUser( user, pass );

  QHttpRequestHeader header( QLatin1String("GET"), ensureFrontBackslash( url.path() ) );
  QString hostport = url.host();
  if (url.port()>0) hostport += ":" + QString("%1").arg( url.port() );
  header.setValue( "Host", hostport );
  header.setValue(QLatin1String("Accept"), QLatin1String("text/xml,application/xml"));
  header.setValue(QLatin1String("User-Agent"), QLatin1String("Bisque AccessC++ with Trolltech Qt"));  
  //header.setValue(QLatin1String("Keep-Alive"), QLatin1String("300"));
  //header.setValue(QLatin1String("Connection"), QLatin1String("Keep-Alive"));
  
  QString authorization = user + ":" + pass;
  authorization = authorization.toLatin1().toBase64();
  header.setValue( QLatin1String("Authorization"), QLatin1String("Basic ") + authorization );

  stop_request = false;
  QTime stopWatch;
  stopWatch.start();
  
  int r = http.request( header, (QIODevice *) 0, iod  );
  requests.insert( r, false );

  while ( requests[r]==false && !stop_request ) {
    if (stopWatch.elapsed() > timeout) { http.abort(); break; }
    QApplication::processEvents();
    QSleepyThread::doMSleep( BQ_SLEEP );
  }
  requests.take( r );
  stop_request = false;
  emit dataReadProgress(100, 100);

  QHttpResponseHeader h = http.lastResponse();
  if ( http.error()==QHttp::NoError && h.statusCode()==200 )
    return 0;  
  else
    return 1;
}

QByteArray BQAccessBase::request( const QUrl &url, int timeout ) {

  QBuffer buffer;
  buffer.open(QBuffer::ReadWrite);

  if ( request(url, &buffer, timeout) == 0 )
    return buffer.buffer();  
  else
    return buffer.buffer();  
}

void BQAccessBase::setHost( const QUrl &v ) { 
  hostUrl = v; 
  if (hostUrl.scheme().isEmpty()) 
    hostUrl.setScheme("http");
}

//---------------------------------------------------------------------------
// BQAccess
//---------------------------------------------------------------------------

BQAccess::BQAccess():BQAccessBase() {
}

BQImageList BQAccess::getImages( const QString &query ) {
  BQImageList images;
  QUrl url( hostUrl );
  url.setPath( "/ds/images?tag_query="+QUrl::toPercentEncoding( query ) );
  QString xml = request( url, BQ_TIMEOUT );

  QDomDocument doc("mydocument");
  if ( doc.setContent(xml) ) {
    QDomElement root = doc.documentElement();
    QDomElement node = root.firstChildElement("image");
    while ( !node.isNull() ) {
      images << BQImageItem(node);
      node = node.nextSiblingElement("image");
    } // while
  }
  return images;
}

BQImageItem BQAccess::getImage( const QUrl &url ) {
  BQImageItem image;
  QString xml = request( url, BQ_TIMEOUT );

  QDomDocument doc("mydocument");
  if ( doc.setContent(xml) ) {
    QDomElement root = doc.documentElement();
    QDomElement node = root.firstChildElement("image");
    if ( !node.isNull() ) {
      image = BQImageItem(node);
    } // while
  }
  return image;
}

QHash<QString, QString> BQAccess::getImageTags( const QUrl &url ) {
  QHash<QString, QString> tags;
  QUrl imgurl( url );
  QString path = url.path() + "/tags";
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

QString BQAccess::getImageGObjects( const QUrl &url ) {

  QUrl imgurl( url );
  QString path = url.path() + "/gobjects?view=deep,canonical";
  imgurl.setPath( path );
  return request( imgurl, BQ_TIMEOUT );
}

int BQAccess::getImageGObjects( const QUrl &url, const QString &fileName ) {
  QUrl imgurl( url );
  QString path = url.path() + "/gobjects?view=deep,canonical";
  imgurl.setPath( path );
  QFile file( fileName );
  return request( imgurl, &file, BQ_TIMEOUT );
}

QString BQAccess::getImageFileName( const QUrl &url ) {
  QUrl imgurl( url );
  QString path = url.path() + "?filename";
  imgurl.setPath( path );
  QString xml = request( imgurl, BQ_TIMEOUT );
  QString fileName;

  QDomDocument doc("mydocument");
  if ( doc.setContent(xml) ) {
    QDomElement root = doc.documentElement();
    QDomElement node = root.firstChildElement("image");
    node = node.firstChildElement("tag");
    if ( !node.isNull() ) {
      QString name, value;
      if (node.hasAttribute("name")) name = node.attribute("name");
      if (node.hasAttribute("value")) value = node.attribute("value");
      if (name == "filename") fileName = value;
    } // while
  }

  if (fileName.isEmpty()) {
    fileName = "bisquik_image_" + QUrl::toPercentEncoding ( url.toString(), QByteArray(), "/" );
  }

  return fileName;
}

QPixmap BQAccess::getImageThumbnail( const QUrl &url ) {
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

int BQAccess::getImageFile( const QUrl &url, const QString &fileName ) {
  //content-disposition: attachment; filename="161pkcvampz1Live2-17-2004_11-57-21_AM.tif"
  QFile file( fileName );
  return request( url, &file, BQ_TIMEOUT );
}

//---------------------------------------------------------------------------
// BQImageItem
//---------------------------------------------------------------------------

BQImageItem::BQImageItem( const QDomElement &node ) {
  fromXML( node );
}

void BQImageItem::fromXML( const QDomElement &node ) {
  perm=0; t=0; y=0; x=0; z=0; ch=0;

  if (node.hasAttribute("uri")) uri = node.attribute("uri");
  if (node.hasAttribute("src")) src = node.attribute("src");

  if (node.hasAttribute("perm")) perm = node.attribute("perm").toInt();
  if (node.hasAttribute("x")) x = node.attribute("x").toInt();
  if (node.hasAttribute("y")) y = node.attribute("y").toInt();
  if (node.hasAttribute("z")) z = node.attribute("z").toInt();
  if (node.hasAttribute("t")) t = node.attribute("t").toInt();
  if (node.hasAttribute("ch")) ch = node.attribute("ch").toInt();
  if (node.hasAttribute("ts")) ts = QDateTime::fromString( node.attribute("ts"), "yyyy-MM-dd HH:mm:ss" );
}

QString BQImageItem::toString(const QUrl &u) const {
  QString text;
  text.sprintf(" ( %dx%dx%dx%dx%d )", x, y, z, t, ch );
  QString url = uri;
  text = url.remove( 0, u.toString().size() ) + text;
  return text;
}

//---------------------------------------------------------------------------
// BQImageList
//---------------------------------------------------------------------------

QStringList BQImageList::toStringList( const QUrl &u ) const {
  QStringList ls;
  for (int i=0; i<this->size(); ++i)
    ls << (*this)[i].toString(u);
  return ls;
}


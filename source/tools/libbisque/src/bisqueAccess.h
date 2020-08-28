#ifndef BISQUE_ACCESS_H
#define BISQUE_ACCESS_H

#include <ui_bisqueAccess.h>

#include <QtCore>
#include <QtGui>
#include <QtNetwork>
#include <QtXml>

#define BQ_TIMEOUT 50000

namespace BQ {

//---------------------------------------------------------------------------
// BQUrl
//---------------------------------------------------------------------------

//"bioview3d://resource/?user=name&pass=pass&url=http://URL/ds/images/1073&gobjects=http://URL/ds/images/1073"

class Url {
public:
  Url() {}
  Url( const QString & );

  bool isNull() const { return protocol().isEmpty(); }
  QString argument( const QString & ) const;

  QString protocol() const { return u.scheme(); }
  QString command() const  { return u.host(); }
  QString user() const     { return u.queryItemValue( "user" ); }
  QString password() const { return u.queryItemValue( "pass" ); }
  
  QUrl    url() const      { return QUrl(argument("url")); }
  QUrl    gobjects() const { return QUrl(argument("gobjects")); }

protected:
  QUrl    u;
};

//---------------------------------------------------------------------------
// NetworkAccessManager - required to authenticate and access SSL secure sites
//---------------------------------------------------------------------------

#ifndef QT_NO_OPENSSL
    typedef int QSslError;
#endif

class NetworkAccessManager : public QNetworkAccessManager
{
    Q_OBJECT

public:
    NetworkAccessManager(QObject *parent = 0);
    void setUserName ( const QString &v ) { this->user = v; }
    void setPassword ( const QString &v ) { this->pass = v; }

private:
    QList<QString> sslTrustedHostList;
    QString user;
    QString pass;

private slots:
    void sslErrors(QNetworkReply *reply, const QList<QSslError> &error);
    void provideAuthentication(QNetworkReply *reply, QAuthenticator *auth);
};

//---------------------------------------------------------------------------
// BQ::NetworkReply
//---------------------------------------------------------------------------

class NetworkReply: public QObject
{
  Q_OBJECT

public:
  NetworkReply( QNetworkReply *reply, QIODevice *iod );
  ~NetworkReply();

  QNetworkReply::NetworkError getError() const { return reply->error(); }
  bool isRunning() const { return reply->isRunning(); }
  int  timeElapsed() const { return stopWatch.elapsed(); }  
  void abort() { reply->abort(); }

signals:
  void dataReadProgress ( qint64 done, qint64 total );  

private slots:
  void onReadProgress ( qint64 bytesReceived, qint64 bytesTotal );
  void onReadyRead ();
  void onError ( QNetworkReply::NetworkError );

protected:
  QNetworkReply *reply;
  QIODevice     *iod;
  QTime          stopWatch;
};

//---------------------------------------------------------------------------
// AccessBase
//---------------------------------------------------------------------------

class QSleepyThread: public QThread
{
  Q_OBJECT
  public:
    QSleepyThread(QObject * parent = 0): QThread(parent) {}
    static void doMSleep(unsigned long  msec) { QThread::msleep(msec); }
};

class AccessBase: public QObject
{
  Q_OBJECT

public:
  AccessBase();
  AccessBase(const QUrl &url, const QString &user, const QString &pass );

  QUrl    host()       const { return hostUrl; }
  QUrl    currentUrl() const { return current_url; }
  QString userName()   const { return user; }
  QString password()   const { return pass; }

  void setHost     ( const QUrl &v );
  void setUserName ( const QString &v ) { user = v; }
  void setPassword ( const QString &v ) { pass = v; }
  QNetworkReply::NetworkError getError() const { return lasterror; }

  inline NetworkAccessManager *getNetworkManager() { return net; } 

  int           request( const QUrl &url, QIODevice *iod, int timeout=BQ_TIMEOUT );
  QByteArray    request( const QUrl &url, int timeout=BQ_TIMEOUT );

public slots:
  void abort() { stop_request = true; QApplication::processEvents(); }

signals:
  void dataReadProgress ( int done, int total );  

private slots:
  void onReadProgress ( qint64 bytesReceived, qint64 bytesTotal );
  void onReplyFinished (QNetworkReply*);

protected:
  NetworkAccessManager *net;

  bool    stop_request;
  unsigned char done_incremental;
  QUrl    hostUrl;
  QUrl    current_url;
  QString user;
  QString pass;
  QTime   progress;
  QNetworkReply::NetworkError lasterror;

private:
  void init();
};



//---------------------------------------------------------------------------
// BQImageItem
//---------------------------------------------------------------------------
/*
class ImageItem {
public:
  QString uri;
  QString src;
  QString name;
  QDateTime ts;
  int perm, t, y, x, z, ch;

  ImageItem() { perm=0; t=0; y=0; x=0; z=0; ch=0; }
  ImageItem( const QDomElement &node );

  bool isNull() const { return uri.isEmpty(); }
  void fromXML( const QDomElement &node );
  QString toString( const QUrl &u = QUrl() ) const;
};

class ImageList: public QList<ImageItem> {
public:
  QStringList toStringList( const QUrl &u = QUrl() ) const;
};
*/

//---------------------------------------------------------------------------
// Access
//---------------------------------------------------------------------------

/*
class Access: public AccessBase
{
  Q_OBJECT

public:
  typedef QHash<QString, QString> BQTags;

  Access();

  QString     getObject( const QUrl &url );
  int         getObject( const QUrl &url, const QString &fileName );

  ImageList   getImages( const QString &query );
  ImageItem   getImage( const QUrl &url );
  BQTags      getImageTags( const QUrl &url );
  QString     getImageGObjects( const QUrl &url );
  QPixmap     getImageThumbnail( const QUrl &url );
  int         getImageFile( const QUrl &url, const QString &fileName );
  int         getImageGObjects( const QUrl &url, const QString &fileName );

  QString     getGObjects( const QUrl &url );
  int         getGObjects( const QUrl &url, const QString &fileName );
};
*/

//---------------------------------------------------------------------------
// BQAccessDialog
//---------------------------------------------------------------------------
/*
class AccessDialog : public QDialog
{
  Q_OBJECT

public:
  AccessDialog();

public slots:
  void onSearch();  
  void onDownload(); 
  void onReject();
  void onAccept();

  void setPath( const QString &v ) { file_path = v; ui.pathLabel->setText( "<a href='#path'>Downloading to: </a>"+file_path ); }

  QString downloadPath() const { return file_path; }
  QString imageFileName() const { return image_file_name; }
  QString gobFileName()   const { return gob_file_name; }

  void startProcess();
  void inProcess( int done, int total, const QString &text );
  void finishProcess();

private:
  Ui::BisqueAccessDialog ui;
  
  Access bqAccess;
  ImageList images;

  QTime time_progress;
  int currentRow;
  QString file_path;
  QString image_file_name, gob_file_name;

  void showErrors();
  void showRequest( const QString & );

private slots:
  void onItemActivated ( QListWidgetItem * item );
  void onHttpReadProgress ( int done, int total );
  void onPathLabelLinkActivated ( const QString & link );
};
*/

//---------------------------------------------------------------------------
// BQAccessWrapper
//---------------------------------------------------------------------------

class AccessWrapper : public QObject
{
  Q_OBJECT

public:
  AccessWrapper();

  void setPath( const QString &v ) { file_path = v; }

  QString downloadPath() const { return file_path; }
  QString imageFileName() const { return image_file_name; }
  QString gobFileName()   const { return gob_file_name; }

public slots:
  bool doDownload( const QUrl &image, const QUrl &gobjects = QUrl() ); 
  void doCancel( ) { bqAccess.abort(); } 

  void setUserName ( const QString &s ) { bqAccess.setUserName(s); }
  void setPassword ( const QString &s ) { bqAccess.setPassword(s); }

signals:
  void startProcess();
  void inProcess( const QString &, unsigned int done, unsigned int total );
  void finishProcess();

private:
  AccessBase bqAccess;
  QString file_path;
  QString image_file_name, gob_file_name;

private slots:
  void onHttpReadProgress ( int done, int total );
};


} // namespace BQ

#endif

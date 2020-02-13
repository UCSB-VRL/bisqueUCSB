#ifndef BISQUIK_ACCESS_H
#define BISQUIK_ACCESS_H

#include <ui_bisquikAccess.h>

#include <QtCore>
#include <QtGui>
#include <QtNetwork>
#include <QtXml>

//---------------------------------------------------------------------------
// BQAccessBase
//---------------------------------------------------------------------------

class BQAccessBase: public QObject
{
  Q_OBJECT

public:
  BQAccessBase();

  QUrl    host()       const { return hostUrl; }
  QUrl    currentUrl() const { return current_url; }
  QString userName()   const { return user; }
  QString password()   const { return pass; }

  void setHost     ( const QUrl &v );
  void setUserName ( const QString &v ) { user = v; }
  void setPassword ( const QString &v ) { pass = v; }
  
  inline QHttp *getHttp() { return &http; } 

  int           request( const QUrl &url, QIODevice *iod, int timeout );
  QByteArray    request( const QUrl &url, int timeout );

public slots:
  void abort() { stop_request = true; QApplication::processEvents(); }

signals:
  void dataReadProgress ( int done, int total );  

private slots:
  void onHttpReadProgress ( int done, int total ) { emit dataReadProgress ( done, total ); }
  void onRequestFinished ( int id, bool /*error*/ ) { requests[id] = true;  }

protected:
  QHttp   http;
  bool    stop_request;
  QUrl    hostUrl;
  QUrl    current_url;
  QString user;
  QString pass;

  QHash< int, bool > requests;
};

//---------------------------------------------------------------------------
// BQImageItem
//---------------------------------------------------------------------------

class BQImageItem {
public:
  QString uri;
  QString src;
  QDateTime ts;
  int perm, t, y, x, z, ch;

  BQImageItem() { perm=0; t=0; y=0; x=0; z=0; ch=0; }
  BQImageItem( const QDomElement &node );

  bool isNull() const { return uri.isEmpty(); }
  void fromXML( const QDomElement &node );
  QString toString( const QUrl &u = QUrl() ) const;
};

class BQImageList: public QList<BQImageItem> {
public:
  QStringList toStringList( const QUrl &u = QUrl() ) const;
};

//---------------------------------------------------------------------------
// BQAccess
//---------------------------------------------------------------------------

class BQAccess: public BQAccessBase
{
  Q_OBJECT

public:
  typedef QHash<QString, QString> BQTags;

  BQAccess();

  BQImageList getImages( const QString &query );
  BQImageItem getImage( const QUrl &url );
  BQTags      getImageTags( const QUrl &url );
  QString     getImageGObjects( const QUrl &url );
  QString     getImageFileName( const QUrl &url );
  QPixmap     getImageThumbnail( const QUrl &url );
  int         getImageFile( const QUrl &url, const QString &fileName );
  int         getImageGObjects( const QUrl &url, const QString &fileName );

};

//---------------------------------------------------------------------------
// BQAccessDialog
//---------------------------------------------------------------------------

class BQAccessDialog : public QDialog
{
  Q_OBJECT

public:
  BQAccessDialog();

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
  Ui::BisquikAccessDialog ui;
  
  BQAccess bqAccess;
  BQImageList images;

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

class QSleepyThread: public QThread
{
  Q_OBJECT
  public:
    QSleepyThread(QObject * parent = 0): QThread(parent) {}
    static void doMSleep(unsigned long  msec) { QThread::msleep(msec); }
};


#endif

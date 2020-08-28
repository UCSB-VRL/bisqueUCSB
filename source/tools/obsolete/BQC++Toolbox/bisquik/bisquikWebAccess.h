#ifndef BISQUIK_WEB_ACCESS_H
#define BISQUIK_WEB_ACCESS_H

#include <ui_bisquikWebAccess.h>

#include <QtCore>
#include <QtGui>
#include <QtNetwork>
#include <QtXml>

#include "bisquikAccess.h"

//---------------------------------------------------------------------------
// BQWebAccessDialog
//---------------------------------------------------------------------------

class BQWebAccessDialog : public QDialog
{
  Q_OBJECT

public:
  BQWebAccessDialog();
  ~BQWebAccessDialog();

public slots:
  void onSearch();  
  void onReject();
  void onAccept();
  void onDownload();

  void setPath( const QString &v ) { file_path = v; ui.pathLabel->setText( "<a href='#path'>Downloading to: </a>"+file_path ); }

  QString downloadPath() const { return file_path; }
  QString imageFileName() const { return image_file_name; }
  QString gobFileName()   const { return gob_file_name; }

  void startProcess();
  void inProcess( int done, int total, const QString &text );
  void finishProcess();

private:
  Ui::BisquikWebAccessDialog ui;
  BQAccess bqAccess;

  QTime time_progress;
  QString file_path;
  QString image_file_name, gob_file_name;

  void showErrors();
  void showRequest( const QString & );

private slots:
  void doDownload( const QUrl & url ); 

  void onWebReadProgress ( int done );
  void onHttpReadProgress ( int done, int total );
  void onUrlChanged ( const QUrl & url );
  void onPathLabelLinkActivated ( const QString & link );
};


#endif // BISQUIK_WEB_ACCESS_H

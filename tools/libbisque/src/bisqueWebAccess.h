/*******************************************************************************

BQ::WebAccessDialog - download dialog in a form of a mini web browser 

Author: Dima Fedorov Levit <dimin@dimin.net> <http://www.dimin.net/>
        Center for Bio-image Informatics, UCSB

History:
2008-01-01 17:02 - First creation

ver: 2

*******************************************************************************/

#ifndef BISQUE_WEB_ACCESS_H
#define BISQUE_WEB_ACCESS_H

#include <ui_bisqueWebAccess.h>

#include <QtCore>
#include <QtXml>
#include <QtNetwork>
#include <QtNetwork/QNetworkAccessManager>
#include <QtNetwork/QNetworkRequest>
#if (QT_VERSION >= QT_VERSION_CHECK(5, 0, 0))
#include <QtWidgets>
#include <QtWebKit>
#include <QtWebKitWidgets>
//#include <QWebView>
#else
#include <QtGui>
#include <QWebView>
#endif

#include "bisqueAccess.h"

namespace BQ {

//---------------------------------------------------------------------------
// WebAccessDialog
//---------------------------------------------------------------------------

class WebView;

class WebAccessDialog : public QDialog
{
  Q_OBJECT

public:
  WebAccessDialog();
  ~WebAccessDialog();

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
  Ui::BisqueWebAccessDialog ui;
  AccessBase bqAccess;
  NetworkAccessManager netman;
  WebView *webView;

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
  void onLinkClicked ( const QUrl & url );
  void onPathLabelLinkActivated ( const QString & link );
};

//---------------------------------------------------------------------------
// BQ::WebView required for the webview to access SSL secure sites
//---------------------------------------------------------------------------

class WebView : public QWebView {
    Q_OBJECT

public:
    WebView(QWidget *parent = 0);

//protected:
//    QWebView* createWindow ( QWebPage::WebWindowType type );
};

class WebPage: public QWebPage {
    Q_OBJECT

public:
    WebPage(QWidget *parent = 0);

protected:
    QWebPage* createWindow ( QWebPage::WebWindowType type );
};

} // namespace BQ

#endif // BISQUE_WEB_ACCESS_H

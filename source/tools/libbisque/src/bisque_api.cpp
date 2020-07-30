/*******************************************************************************

  Bisque API

  Author: Dima Fedorov Levit <dimin@dimin.net> <http://www.dimin.net/>

  History:
     2013-04-25 13:35:18 - First creation
      
  ver: 2
        
*******************************************************************************/

#include <QtCore>
#include <QtXml>

#include "bisque_api.h"
#include "BisqueAccess.h"


//---------------------------------------------------------------------------
// BQ::Factory
//---------------------------------------------------------------------------

template <class T>
BQ::Node* CreateObject(const QSharedPointer<QDomDocument> &doc, const QDomElement &node, const QString &user, const QString &pass) { 
    return new T(doc, node, user, pass); 
}

BQ::Factory::ClassRegistry BQ::Factory::registry = BQ::Factory::init();
BQ::Factory::ClassRegistry BQ::Factory::init() {
    BQ::Factory::ClassRegistry r;
    r["node"]  =  &CreateObject<BQ::Node>;
    r["file"]  =  &CreateObject<BQ::File>;
    r["image"] =  &CreateObject<BQ::Image>;
    return r;
}

BQ::Node* BQ::Factory::fetch( const QSharedPointer<QDomDocument> &doc, const QDomElement &node, const QString &user, const QString &pass ) {
    QString type = node.tagName();
    qDebug( type.toLatin1().constData() );
    if (registry.find(type) == registry.end())
        type = "node";
    return registry[type](doc, node, user, pass);
}

BQ::Node* BQ::Factory::fetch( const QUrl &url, const QString &user, const QString &pass ) {
    BQ::AccessBase access(QUrl(), user, pass);
    QString xml = access.request( QUrl(url) );
    QSharedPointer<QDomDocument> doc = QSharedPointer<QDomDocument>(new QDomDocument("bqdoc"));
    if ( doc->setContent(xml) ) {
        QDomElement element = doc->documentElement();
        return BQ::Factory::fetch( doc, element, user, pass );
    }
    return 0;
}

//---------------------------------------------------------------------------
// BQ::Node
//---------------------------------------------------------------------------

BQ::Node::Node( const QSharedPointer<QDomDocument> &doc, const QDomElement &node, const QString &user, const QString &pass ) {
    this->doc = doc;
    this->element = node;
    this->user = user;
    this->pass = pass;
}

BQ::Node::Node( const QUrl &url, const QString &user, const QString &pass ) {
    this->user = user;
    this->pass = pass;
    if (url.isEmpty()) return;
    BQ::AccessBase access(QUrl(), this->user, this->pass);
    QString xml = access.request( QUrl(url) );
    qDebug( xml.toLatin1().constData() );
    this->doc = QSharedPointer<QDomDocument>(new QDomDocument("bqdoc"));
    if ( doc->setContent(xml) ) {
        this->element = doc->documentElement();
    }
}

BQ::Node::~Node() {
    this->doc.clear();
}

QString BQ::Node::toString() const {
    QString str;
    QTextStream stream(&str);
    this->element.save(stream, 4);    
    return str;
}

int BQ::Node::fetch( const QString &fileName ) {
    qDebug( fileName.toLatin1().constData() );
    QString str = this->toString();
    QFile f(fileName);
    f.open(QIODevice::WriteOnly);
    //QTextStream out(&file);
    f.write( str.toUtf8() );
    f.close(); 
    return 0;
}

BQ::Node BQ::Node::findNode(const QString &expression) const {
  return BQ::Node(QUrl());
  // dima: no Xpath in QT over DOM ????
    /*
    QXmlQuery query;
    //query.setFocus(&file);
    query.setQuery(expression);

    QXmlResultItems results;

 if (query.isValid()) {
     query.evaluateTo(&result);
     QXmlItem item(result.next());
     while (!item.isNull()) {
         // use item
         item = result.next();
     }
     if (result.hasError())
         /* Runtime error! */


   /*
   QXmlSerializer serializer(query, myOutputDevice);
   query.evaluateTo(&serializer);


            import javax.xml.xpath.*;
            factory = XPathFactory.newInstance;
            xpath = factory.newXPath;    
            xn = xpath.evaluate(expression, self.element, XPathConstants.NODE);
            if ~isempty(xn),
                node = bq.Factory.fetch(self.doc, xn, self.user, self.password);
            else
                node = [];
            end
        end    
*/
}

//---------------------------------------------------------------------------
// BQ::File
//---------------------------------------------------------------------------

BQ::File::File( const QSharedPointer<QDomDocument> &doc, const QDomElement &node, const QString &user, const QString &pass ):
  BQ::Node( doc, node, user, pass ) {

}

BQ::File::File( const QUrl &url, const QString &user, const QString &pass ): 
  BQ::Node( url, user, pass ) {

}

int BQ::File::fetch( const QString &fileName ) {
    qDebug( fileName.toLatin1().constData() );
    QFile file( fileName );
    file.open( QIODevice::WriteOnly );

    QString uri = this->getAttribute("uri");
    QString uniq = this->getAttribute("resource_uniq");
    QUrl url(uri);
    url.setPath( QString("/image_service/") + uniq );
    
    BQ::AccessBase access(QUrl(), this->user, this->pass);
    int r = access.request( url, &file );
    file.flush();
    file.close();
    return r;
}

//---------------------------------------------------------------------------
// BQ::Image
//---------------------------------------------------------------------------

BQ::Image::Image( const QSharedPointer<QDomDocument> &doc, const QDomElement &node, const QString &user, const QString &pass ):
  BQ::File( doc, node, user, pass ) {

}

BQ::Image::Image( const QUrl &url, const QString &user, const QString &pass ): 
  BQ::File( url, user, pass ) {

}

//int BQ::Image::fetch( const QString &fileName ) {
//}

QPixmap BQ::Image::getThumbnail() const {
    QString uri = this->getAttribute("uri");
    QString uniq = this->getAttribute("resource_uniq");
    QUrl url(uri);
    url.setPath( QString("/image_service/") + uniq );

    QList<QByteArray> fl= QImageReader::supportedImageFormats();
    if (fl.indexOf("JPEG")==-1) { // If Qt does not have jpeg reader
        url.addQueryItem("slice", ",,1,1&remap=display&resize=200,200,BC,AR&format=bmp");
    } else {
        url.addQueryItem("thumbnail", "200,200,BC");
    }

    QBuffer buffer;
    buffer.open(QBuffer::ReadWrite);
    QPixmap image;
    BQ::AccessBase access(QUrl(), this->user, this->pass);
    if (access.request( url, &buffer ) == 0)
        image.loadFromData( buffer.buffer() );
    return image;
}

//---------------------------------------------------------------------------
// BQ::Session
//---------------------------------------------------------------------------




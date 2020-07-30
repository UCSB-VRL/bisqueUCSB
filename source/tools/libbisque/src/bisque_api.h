/*******************************************************************************

  Bisque API

  Author: Dima Fedorov Levit <dimin@dimin.net> <http://www.dimin.net/>

  History:
     2013-04-25 13:35:18 - First creation
      
  ver: 2
        
*******************************************************************************/

#ifndef BISQUE_API_H
#define BISQUE_API_H

#include <QtCore>
#include <QtXml>

namespace BQ {

class Node;
class File;
class Image;

//---------------------------------------------------------------------------
// BQ::Factory
//---------------------------------------------------------------------------

class Factory {
public:
    static Node* fetch( const QSharedPointer<QDomDocument> &doc, const QDomElement &node, const QString &user=QString(), const QString &pass=QString() );
    static Node* fetch( const QUrl &url=QUrl(), const QString &user=QString(), const QString &pass=QString() );
private:
    typedef std::map<QString, Node* (*)(const QSharedPointer<QDomDocument> &doc, const QDomElement &node, const QString &user, const QString &pass)> ClassRegistry;
    static ClassRegistry registry;
public:
    static ClassRegistry init();
};

//---------------------------------------------------------------------------
// BQ::Node
//---------------------------------------------------------------------------

class Node {
public:
    Node( const QSharedPointer<QDomDocument> &doc, const QDomElement &node, const QString &user=QString(), const QString &pass=QString() );
    Node( const QUrl &url=QUrl(), const QString &user=QString(), const QString &pass=QString() );
    ~Node();

    //bool isNull() const { return uri.isEmpty(); }
    QString toString() const;

    QString getAttribute(const QString &name, const QString & defValue = QString() ) const { return element.attribute(name, defValue); }
    bool    hasAttribute(const QString &name) const { return element.hasAttribute(name); }
    void    setAttribute(const QString &name, const QString &value ) { element.setAttribute(name, value); }

    void    setValue(const QString &value ) { element.setAttribute("value", value); }
    // dima: getValue needs to parse type and return proper QVariant
    QString getValue(const QString &defValue = QString() ) const { return element.attribute("value", defValue); } 

    Node    findNode(const QString &expression)  const; // use XPATH expresssion to find a node

    int fetch( const QString &fileName );

protected:
    QSharedPointer<QDomDocument> doc;
    QDomElement element;
    QString user;
    QString pass;
};

//---------------------------------------------------------------------------
// BQ::File
//---------------------------------------------------------------------------

class File: public Node {
public:
    File( const QSharedPointer<QDomDocument> &doc, const QDomElement &node, const QString &user=QString(), const QString &pass=QString() );
    File( const QUrl &url=QUrl(), const QString &user=QString(), const QString &pass=QString() );

    int fetch( const QString &fileName );
};

//---------------------------------------------------------------------------
// BQ::Image
//---------------------------------------------------------------------------

class Image: public File {
public:
    Image( const QSharedPointer<QDomDocument> &doc, const QDomElement &node, const QString &user=QString(), const QString &pass=QString() );
    Image( const QUrl &url=QUrl(), const QString &user=QString(), const QString &pass=QString() );

    //int fetch( const QString &fileName );
    QPixmap getThumbnail() const;
};

} // namespace BQ


//---------------------------------------------------------------------------
// BQ::Session
//---------------------------------------------------------------------------



#endif // BISQUE_API_H

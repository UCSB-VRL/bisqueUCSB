/****************************************************************************
** Meta object code from reading C++ file 'bisqueWebAccess.h'
**
** Created: Fri Jun 21 14:56:03 2013
**      by: The Qt Meta Object Compiler version 63 (Qt 4.8.4)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../src/bisqueWebAccess.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'bisqueWebAccess.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 63
#error "This file was generated using the moc from 4.8.4. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_BQ__WebAccessDialog[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
      17,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: signature, parameters, type, tag, flags
      21,   20,   20,   20, 0x0a,
      32,   20,   20,   20, 0x0a,
      43,   20,   20,   20, 0x0a,
      54,   20,   20,   20, 0x0a,
      69,   67,   20,   20, 0x0a,
      94,   20,   86,   20, 0x0a,
     109,   20,   86,   20, 0x0a,
     125,   20,   86,   20, 0x0a,
     139,   20,   20,   20, 0x0a,
     170,  154,   20,   20, 0x0a,
     197,   20,   20,   20, 0x0a,
     217,  213,   20,   20, 0x08,
     239,  234,   20,   20, 0x08,
     273,  262,   20,   20, 0x08,
     301,  213,   20,   20, 0x08,
     320,  213,   20,   20, 0x08,
     345,  340,   20,   20, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_BQ__WebAccessDialog[] = {
    "BQ::WebAccessDialog\0\0onSearch()\0"
    "onReject()\0onAccept()\0onDownload()\0v\0"
    "setPath(QString)\0QString\0downloadPath()\0"
    "imageFileName()\0gobFileName()\0"
    "startProcess()\0done,total,text\0"
    "inProcess(int,int,QString)\0finishProcess()\0"
    "url\0doDownload(QUrl)\0done\0"
    "onWebReadProgress(int)\0done,total\0"
    "onHttpReadProgress(int,int)\0"
    "onUrlChanged(QUrl)\0onLinkClicked(QUrl)\0"
    "link\0onPathLabelLinkActivated(QString)\0"
};

void BQ::WebAccessDialog::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        WebAccessDialog *_t = static_cast<WebAccessDialog *>(_o);
        switch (_id) {
        case 0: _t->onSearch(); break;
        case 1: _t->onReject(); break;
        case 2: _t->onAccept(); break;
        case 3: _t->onDownload(); break;
        case 4: _t->setPath((*reinterpret_cast< const QString(*)>(_a[1]))); break;
        case 5: { QString _r = _t->downloadPath();
            if (_a[0]) *reinterpret_cast< QString*>(_a[0]) = _r; }  break;
        case 6: { QString _r = _t->imageFileName();
            if (_a[0]) *reinterpret_cast< QString*>(_a[0]) = _r; }  break;
        case 7: { QString _r = _t->gobFileName();
            if (_a[0]) *reinterpret_cast< QString*>(_a[0]) = _r; }  break;
        case 8: _t->startProcess(); break;
        case 9: _t->inProcess((*reinterpret_cast< int(*)>(_a[1])),(*reinterpret_cast< int(*)>(_a[2])),(*reinterpret_cast< const QString(*)>(_a[3]))); break;
        case 10: _t->finishProcess(); break;
        case 11: _t->doDownload((*reinterpret_cast< const QUrl(*)>(_a[1]))); break;
        case 12: _t->onWebReadProgress((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 13: _t->onHttpReadProgress((*reinterpret_cast< int(*)>(_a[1])),(*reinterpret_cast< int(*)>(_a[2]))); break;
        case 14: _t->onUrlChanged((*reinterpret_cast< const QUrl(*)>(_a[1]))); break;
        case 15: _t->onLinkClicked((*reinterpret_cast< const QUrl(*)>(_a[1]))); break;
        case 16: _t->onPathLabelLinkActivated((*reinterpret_cast< const QString(*)>(_a[1]))); break;
        default: ;
        }
    }
}

const QMetaObjectExtraData BQ::WebAccessDialog::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject BQ::WebAccessDialog::staticMetaObject = {
    { &QDialog::staticMetaObject, qt_meta_stringdata_BQ__WebAccessDialog,
      qt_meta_data_BQ__WebAccessDialog, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &BQ::WebAccessDialog::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *BQ::WebAccessDialog::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *BQ::WebAccessDialog::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_BQ__WebAccessDialog))
        return static_cast<void*>(const_cast< WebAccessDialog*>(this));
    return QDialog::qt_metacast(_clname);
}

int BQ::WebAccessDialog::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QDialog::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 17)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 17;
    }
    return _id;
}
static const uint qt_meta_data_BQ__WebView[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       0,    0, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

       0        // eod
};

static const char qt_meta_stringdata_BQ__WebView[] = {
    "BQ::WebView\0"
};

void BQ::WebView::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    Q_UNUSED(_o);
    Q_UNUSED(_id);
    Q_UNUSED(_c);
    Q_UNUSED(_a);
}

const QMetaObjectExtraData BQ::WebView::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject BQ::WebView::staticMetaObject = {
    { &QWebView::staticMetaObject, qt_meta_stringdata_BQ__WebView,
      qt_meta_data_BQ__WebView, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &BQ::WebView::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *BQ::WebView::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *BQ::WebView::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_BQ__WebView))
        return static_cast<void*>(const_cast< WebView*>(this));
    return QWebView::qt_metacast(_clname);
}

int BQ::WebView::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QWebView::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    return _id;
}
static const uint qt_meta_data_BQ__WebPage[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       0,    0, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

       0        // eod
};

static const char qt_meta_stringdata_BQ__WebPage[] = {
    "BQ::WebPage\0"
};

void BQ::WebPage::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    Q_UNUSED(_o);
    Q_UNUSED(_id);
    Q_UNUSED(_c);
    Q_UNUSED(_a);
}

const QMetaObjectExtraData BQ::WebPage::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject BQ::WebPage::staticMetaObject = {
    { &QWebPage::staticMetaObject, qt_meta_stringdata_BQ__WebPage,
      qt_meta_data_BQ__WebPage, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &BQ::WebPage::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *BQ::WebPage::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *BQ::WebPage::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_BQ__WebPage))
        return static_cast<void*>(const_cast< WebPage*>(this));
    return QWebPage::qt_metacast(_clname);
}

int BQ::WebPage::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QWebPage::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    return _id;
}
QT_END_MOC_NAMESPACE

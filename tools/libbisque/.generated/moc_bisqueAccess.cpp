/****************************************************************************
** Meta object code from reading C++ file 'bisqueAccess.h'
**
** Created: Fri Jun 21 14:56:03 2013
**      by: The Qt Meta Object Compiler version 63 (Qt 4.8.4)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../src/bisqueAccess.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'bisqueAccess.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 63
#error "This file was generated using the moc from 4.8.4. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_BQ__NetworkAccessManager[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       2,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: signature, parameters, type, tag, flags
      38,   26,   25,   25, 0x08,
      92,   81,   25,   25, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_BQ__NetworkAccessManager[] = {
    "BQ::NetworkAccessManager\0\0reply,error\0"
    "sslErrors(QNetworkReply*,QList<QSslError>)\0"
    "reply,auth\0"
    "provideAuthentication(QNetworkReply*,QAuthenticator*)\0"
};

void BQ::NetworkAccessManager::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        NetworkAccessManager *_t = static_cast<NetworkAccessManager *>(_o);
        switch (_id) {
        case 0: _t->sslErrors((*reinterpret_cast< QNetworkReply*(*)>(_a[1])),(*reinterpret_cast< const QList<QSslError>(*)>(_a[2]))); break;
        case 1: _t->provideAuthentication((*reinterpret_cast< QNetworkReply*(*)>(_a[1])),(*reinterpret_cast< QAuthenticator*(*)>(_a[2]))); break;
        default: ;
        }
    }
}

const QMetaObjectExtraData BQ::NetworkAccessManager::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject BQ::NetworkAccessManager::staticMetaObject = {
    { &QNetworkAccessManager::staticMetaObject, qt_meta_stringdata_BQ__NetworkAccessManager,
      qt_meta_data_BQ__NetworkAccessManager, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &BQ::NetworkAccessManager::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *BQ::NetworkAccessManager::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *BQ::NetworkAccessManager::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_BQ__NetworkAccessManager))
        return static_cast<void*>(const_cast< NetworkAccessManager*>(this));
    return QNetworkAccessManager::qt_metacast(_clname);
}

int BQ::NetworkAccessManager::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QNetworkAccessManager::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 2)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 2;
    }
    return _id;
}
static const uint qt_meta_data_BQ__NetworkReply[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       4,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       1,       // signalCount

 // signals: signature, parameters, type, tag, flags
      29,   18,   17,   17, 0x05,

 // slots: signature, parameters, type, tag, flags
      86,   61,   17,   17, 0x08,
     116,   17,   17,   17, 0x08,
     130,   17,   17,   17, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_BQ__NetworkReply[] = {
    "BQ::NetworkReply\0\0done,total\0"
    "dataReadProgress(qint64,qint64)\0"
    "bytesReceived,bytesTotal\0"
    "onReadProgress(qint64,qint64)\0"
    "onReadyRead()\0onError(QNetworkReply::NetworkError)\0"
};

void BQ::NetworkReply::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        NetworkReply *_t = static_cast<NetworkReply *>(_o);
        switch (_id) {
        case 0: _t->dataReadProgress((*reinterpret_cast< qint64(*)>(_a[1])),(*reinterpret_cast< qint64(*)>(_a[2]))); break;
        case 1: _t->onReadProgress((*reinterpret_cast< qint64(*)>(_a[1])),(*reinterpret_cast< qint64(*)>(_a[2]))); break;
        case 2: _t->onReadyRead(); break;
        case 3: _t->onError((*reinterpret_cast< QNetworkReply::NetworkError(*)>(_a[1]))); break;
        default: ;
        }
    }
}

const QMetaObjectExtraData BQ::NetworkReply::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject BQ::NetworkReply::staticMetaObject = {
    { &QObject::staticMetaObject, qt_meta_stringdata_BQ__NetworkReply,
      qt_meta_data_BQ__NetworkReply, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &BQ::NetworkReply::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *BQ::NetworkReply::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *BQ::NetworkReply::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_BQ__NetworkReply))
        return static_cast<void*>(const_cast< NetworkReply*>(this));
    return QObject::qt_metacast(_clname);
}

int BQ::NetworkReply::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 4)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 4;
    }
    return _id;
}

// SIGNAL 0
void BQ::NetworkReply::dataReadProgress(qint64 _t1, qint64 _t2)
{
    void *_a[] = { 0, const_cast<void*>(reinterpret_cast<const void*>(&_t1)), const_cast<void*>(reinterpret_cast<const void*>(&_t2)) };
    QMetaObject::activate(this, &staticMetaObject, 0, _a);
}
static const uint qt_meta_data_BQ__QSleepyThread[] = {

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

static const char qt_meta_stringdata_BQ__QSleepyThread[] = {
    "BQ::QSleepyThread\0"
};

void BQ::QSleepyThread::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    Q_UNUSED(_o);
    Q_UNUSED(_id);
    Q_UNUSED(_c);
    Q_UNUSED(_a);
}

const QMetaObjectExtraData BQ::QSleepyThread::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject BQ::QSleepyThread::staticMetaObject = {
    { &QThread::staticMetaObject, qt_meta_stringdata_BQ__QSleepyThread,
      qt_meta_data_BQ__QSleepyThread, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &BQ::QSleepyThread::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *BQ::QSleepyThread::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *BQ::QSleepyThread::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_BQ__QSleepyThread))
        return static_cast<void*>(const_cast< QSleepyThread*>(this));
    return QThread::qt_metacast(_clname);
}

int BQ::QSleepyThread::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QThread::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    return _id;
}
static const uint qt_meta_data_BQ__AccessBase[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       4,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       1,       // signalCount

 // signals: signature, parameters, type, tag, flags
      27,   16,   15,   15, 0x05,

 // slots: signature, parameters, type, tag, flags
      53,   15,   15,   15, 0x0a,
      86,   61,   15,   15, 0x08,
     116,   15,   15,   15, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_BQ__AccessBase[] = {
    "BQ::AccessBase\0\0done,total\0"
    "dataReadProgress(int,int)\0abort()\0"
    "bytesReceived,bytesTotal\0"
    "onReadProgress(qint64,qint64)\0"
    "onReplyFinished(QNetworkReply*)\0"
};

void BQ::AccessBase::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        AccessBase *_t = static_cast<AccessBase *>(_o);
        switch (_id) {
        case 0: _t->dataReadProgress((*reinterpret_cast< int(*)>(_a[1])),(*reinterpret_cast< int(*)>(_a[2]))); break;
        case 1: _t->abort(); break;
        case 2: _t->onReadProgress((*reinterpret_cast< qint64(*)>(_a[1])),(*reinterpret_cast< qint64(*)>(_a[2]))); break;
        case 3: _t->onReplyFinished((*reinterpret_cast< QNetworkReply*(*)>(_a[1]))); break;
        default: ;
        }
    }
}

const QMetaObjectExtraData BQ::AccessBase::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject BQ::AccessBase::staticMetaObject = {
    { &QObject::staticMetaObject, qt_meta_stringdata_BQ__AccessBase,
      qt_meta_data_BQ__AccessBase, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &BQ::AccessBase::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *BQ::AccessBase::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *BQ::AccessBase::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_BQ__AccessBase))
        return static_cast<void*>(const_cast< AccessBase*>(this));
    return QObject::qt_metacast(_clname);
}

int BQ::AccessBase::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 4)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 4;
    }
    return _id;
}

// SIGNAL 0
void BQ::AccessBase::dataReadProgress(int _t1, int _t2)
{
    void *_a[] = { 0, const_cast<void*>(reinterpret_cast<const void*>(&_t1)), const_cast<void*>(reinterpret_cast<const void*>(&_t2)) };
    QMetaObject::activate(this, &staticMetaObject, 0, _a);
}
static const uint qt_meta_data_BQ__AccessWrapper[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       9,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       3,       // signalCount

 // signals: signature, parameters, type, tag, flags
      19,   18,   18,   18, 0x05,
      46,   34,   18,   18, 0x05,
      75,   18,   18,   18, 0x05,

 // slots: signature, parameters, type, tag, flags
     111,   96,   91,   18, 0x0a,
     139,  133,   91,   18, 0x2a,
     156,   18,   18,   18, 0x0a,
     169,  167,   18,   18, 0x0a,
     190,  167,   18,   18, 0x0a,
     222,  211,   18,   18, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_BQ__AccessWrapper[] = {
    "BQ::AccessWrapper\0\0startProcess()\0"
    ",done,total\0inProcess(QString,uint,uint)\0"
    "finishProcess()\0bool\0image,gobjects\0"
    "doDownload(QUrl,QUrl)\0image\0"
    "doDownload(QUrl)\0doCancel()\0s\0"
    "setUserName(QString)\0setPassword(QString)\0"
    "done,total\0onHttpReadProgress(int,int)\0"
};

void BQ::AccessWrapper::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        AccessWrapper *_t = static_cast<AccessWrapper *>(_o);
        switch (_id) {
        case 0: _t->startProcess(); break;
        case 1: _t->inProcess((*reinterpret_cast< const QString(*)>(_a[1])),(*reinterpret_cast< uint(*)>(_a[2])),(*reinterpret_cast< uint(*)>(_a[3]))); break;
        case 2: _t->finishProcess(); break;
        case 3: { bool _r = _t->doDownload((*reinterpret_cast< const QUrl(*)>(_a[1])),(*reinterpret_cast< const QUrl(*)>(_a[2])));
            if (_a[0]) *reinterpret_cast< bool*>(_a[0]) = _r; }  break;
        case 4: { bool _r = _t->doDownload((*reinterpret_cast< const QUrl(*)>(_a[1])));
            if (_a[0]) *reinterpret_cast< bool*>(_a[0]) = _r; }  break;
        case 5: _t->doCancel(); break;
        case 6: _t->setUserName((*reinterpret_cast< const QString(*)>(_a[1]))); break;
        case 7: _t->setPassword((*reinterpret_cast< const QString(*)>(_a[1]))); break;
        case 8: _t->onHttpReadProgress((*reinterpret_cast< int(*)>(_a[1])),(*reinterpret_cast< int(*)>(_a[2]))); break;
        default: ;
        }
    }
}

const QMetaObjectExtraData BQ::AccessWrapper::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject BQ::AccessWrapper::staticMetaObject = {
    { &QObject::staticMetaObject, qt_meta_stringdata_BQ__AccessWrapper,
      qt_meta_data_BQ__AccessWrapper, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &BQ::AccessWrapper::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *BQ::AccessWrapper::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *BQ::AccessWrapper::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_BQ__AccessWrapper))
        return static_cast<void*>(const_cast< AccessWrapper*>(this));
    return QObject::qt_metacast(_clname);
}

int BQ::AccessWrapper::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 9)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 9;
    }
    return _id;
}

// SIGNAL 0
void BQ::AccessWrapper::startProcess()
{
    QMetaObject::activate(this, &staticMetaObject, 0, 0);
}

// SIGNAL 1
void BQ::AccessWrapper::inProcess(const QString & _t1, unsigned int _t2, unsigned int _t3)
{
    void *_a[] = { 0, const_cast<void*>(reinterpret_cast<const void*>(&_t1)), const_cast<void*>(reinterpret_cast<const void*>(&_t2)), const_cast<void*>(reinterpret_cast<const void*>(&_t3)) };
    QMetaObject::activate(this, &staticMetaObject, 1, _a);
}

// SIGNAL 2
void BQ::AccessWrapper::finishProcess()
{
    QMetaObject::activate(this, &staticMetaObject, 2, 0);
}
QT_END_MOC_NAMESPACE

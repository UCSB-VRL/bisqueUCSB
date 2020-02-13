
#include <QApplication>

#include "bisquik/bisquikAccess.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    BQAccessDialog w;
    w.show();
    return w.exec();
}

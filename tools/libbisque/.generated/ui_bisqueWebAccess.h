/********************************************************************************
** Form generated from reading UI file 'bisqueWebAccess.ui'
**
** Created: Fri Jun 21 14:56:03 2013
**      by: Qt User Interface Compiler version 4.8.4
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_BISQUEWEBACCESS_H
#define UI_BISQUEWEBACCESS_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QCheckBox>
#include <QtGui/QDialog>
#include <QtGui/QDialogButtonBox>
#include <QtGui/QGridLayout>
#include <QtGui/QGroupBox>
#include <QtGui/QHBoxLayout>
#include <QtGui/QHeaderView>
#include <QtGui/QLabel>
#include <QtGui/QLineEdit>
#include <QtGui/QProgressBar>
#include <QtGui/QPushButton>
#include <QtGui/QVBoxLayout>
#include <QtGui/QWidget>

QT_BEGIN_NAMESPACE

class Ui_BisqueWebAccessDialog
{
public:
    QGridLayout *gridLayout_3;
    QGroupBox *groupBox_3;
    QGridLayout *gridLayout;
    QLabel *label;
    QLineEdit *urlEdit;
    QLabel *label_2;
    QLineEdit *userEdit;
    QPushButton *searchButton;
    QLabel *label_3;
    QLineEdit *passwordEdit;
    QWidget *widget;
    QHBoxLayout *hboxLayout;
    QLabel *pathLabel;
    QCheckBox *autoLoadCheck;
    QDialogButtonBox *buttonBox;
    QGroupBox *groupBox;
    QVBoxLayout *verticalLayout;
    QWidget *widget_2;
    QHBoxLayout *hboxLayout1;
    QPushButton *backButton;
    QPushButton *cancelButton;
    QProgressBar *progressBar;
    QLabel *progressLabel;

    void setupUi(QDialog *BisqueWebAccessDialog)
    {
        if (BisqueWebAccessDialog->objectName().isEmpty())
            BisqueWebAccessDialog->setObjectName(QString::fromUtf8("BisqueWebAccessDialog"));
        BisqueWebAccessDialog->resize(892, 748);
        gridLayout_3 = new QGridLayout(BisqueWebAccessDialog);
        gridLayout_3->setSpacing(2);
        gridLayout_3->setContentsMargins(4, 4, 4, 4);
        gridLayout_3->setObjectName(QString::fromUtf8("gridLayout_3"));
        gridLayout_3->setSizeConstraint(QLayout::SetDefaultConstraint);
        groupBox_3 = new QGroupBox(BisqueWebAccessDialog);
        groupBox_3->setObjectName(QString::fromUtf8("groupBox_3"));
        QSizePolicy sizePolicy(QSizePolicy::Preferred, QSizePolicy::Maximum);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(groupBox_3->sizePolicy().hasHeightForWidth());
        groupBox_3->setSizePolicy(sizePolicy);
        gridLayout = new QGridLayout(groupBox_3);
        gridLayout->setSpacing(4);
        gridLayout->setContentsMargins(6, 6, 6, 6);
        gridLayout->setObjectName(QString::fromUtf8("gridLayout"));
        label = new QLabel(groupBox_3);
        label->setObjectName(QString::fromUtf8("label"));
        QSizePolicy sizePolicy1(QSizePolicy::Maximum, QSizePolicy::Preferred);
        sizePolicy1.setHorizontalStretch(0);
        sizePolicy1.setVerticalStretch(0);
        sizePolicy1.setHeightForWidth(label->sizePolicy().hasHeightForWidth());
        label->setSizePolicy(sizePolicy1);

        gridLayout->addWidget(label, 0, 0, 1, 1);

        urlEdit = new QLineEdit(groupBox_3);
        urlEdit->setObjectName(QString::fromUtf8("urlEdit"));

        gridLayout->addWidget(urlEdit, 0, 1, 1, 2);

        label_2 = new QLabel(groupBox_3);
        label_2->setObjectName(QString::fromUtf8("label_2"));
        sizePolicy1.setHeightForWidth(label_2->sizePolicy().hasHeightForWidth());
        label_2->setSizePolicy(sizePolicy1);

        gridLayout->addWidget(label_2, 1, 0, 1, 1);

        userEdit = new QLineEdit(groupBox_3);
        userEdit->setObjectName(QString::fromUtf8("userEdit"));
        userEdit->setMaximumSize(QSize(300, 16777215));

        gridLayout->addWidget(userEdit, 1, 1, 1, 1);

        searchButton = new QPushButton(groupBox_3);
        searchButton->setObjectName(QString::fromUtf8("searchButton"));
        QSizePolicy sizePolicy2(QSizePolicy::Expanding, QSizePolicy::Expanding);
        sizePolicy2.setHorizontalStretch(0);
        sizePolicy2.setVerticalStretch(0);
        sizePolicy2.setHeightForWidth(searchButton->sizePolicy().hasHeightForWidth());
        searchButton->setSizePolicy(sizePolicy2);

        gridLayout->addWidget(searchButton, 1, 2, 2, 1);

        label_3 = new QLabel(groupBox_3);
        label_3->setObjectName(QString::fromUtf8("label_3"));
        sizePolicy1.setHeightForWidth(label_3->sizePolicy().hasHeightForWidth());
        label_3->setSizePolicy(sizePolicy1);

        gridLayout->addWidget(label_3, 2, 0, 1, 1);

        passwordEdit = new QLineEdit(groupBox_3);
        passwordEdit->setObjectName(QString::fromUtf8("passwordEdit"));
        passwordEdit->setMaximumSize(QSize(300, 16777215));
        passwordEdit->setEchoMode(QLineEdit::Password);

        gridLayout->addWidget(passwordEdit, 2, 1, 1, 1);


        gridLayout_3->addWidget(groupBox_3, 0, 0, 1, 1);

        widget = new QWidget(BisqueWebAccessDialog);
        widget->setObjectName(QString::fromUtf8("widget"));
        sizePolicy.setHeightForWidth(widget->sizePolicy().hasHeightForWidth());
        widget->setSizePolicy(sizePolicy);
        hboxLayout = new QHBoxLayout(widget);
        hboxLayout->setSpacing(4);
        hboxLayout->setContentsMargins(4, 4, 4, 4);
        hboxLayout->setObjectName(QString::fromUtf8("hboxLayout"));
        pathLabel = new QLabel(widget);
        pathLabel->setObjectName(QString::fromUtf8("pathLabel"));
        QSizePolicy sizePolicy3(QSizePolicy::Expanding, QSizePolicy::Preferred);
        sizePolicy3.setHorizontalStretch(0);
        sizePolicy3.setVerticalStretch(0);
        sizePolicy3.setHeightForWidth(pathLabel->sizePolicy().hasHeightForWidth());
        pathLabel->setSizePolicy(sizePolicy3);
        pathLabel->setCursor(QCursor(Qt::PointingHandCursor));
        pathLabel->setTextFormat(Qt::RichText);

        hboxLayout->addWidget(pathLabel);

        autoLoadCheck = new QCheckBox(widget);
        autoLoadCheck->setObjectName(QString::fromUtf8("autoLoadCheck"));

        hboxLayout->addWidget(autoLoadCheck);

        buttonBox = new QDialogButtonBox(widget);
        buttonBox->setObjectName(QString::fromUtf8("buttonBox"));
        QSizePolicy sizePolicy4(QSizePolicy::Maximum, QSizePolicy::Fixed);
        sizePolicy4.setHorizontalStretch(0);
        sizePolicy4.setVerticalStretch(0);
        sizePolicy4.setHeightForWidth(buttonBox->sizePolicy().hasHeightForWidth());
        buttonBox->setSizePolicy(sizePolicy4);
        buttonBox->setOrientation(Qt::Horizontal);
        buttonBox->setStandardButtons(QDialogButtonBox::Close|QDialogButtonBox::Open);

        hboxLayout->addWidget(buttonBox);


        gridLayout_3->addWidget(widget, 4, 0, 1, 1);

        groupBox = new QGroupBox(BisqueWebAccessDialog);
        groupBox->setObjectName(QString::fromUtf8("groupBox"));
        verticalLayout = new QVBoxLayout(groupBox);
        verticalLayout->setContentsMargins(4, 4, 4, 4);
        verticalLayout->setObjectName(QString::fromUtf8("verticalLayout"));

        gridLayout_3->addWidget(groupBox, 2, 0, 1, 1);

        widget_2 = new QWidget(BisqueWebAccessDialog);
        widget_2->setObjectName(QString::fromUtf8("widget_2"));
        sizePolicy.setHeightForWidth(widget_2->sizePolicy().hasHeightForWidth());
        widget_2->setSizePolicy(sizePolicy);
        hboxLayout1 = new QHBoxLayout(widget_2);
        hboxLayout1->setSpacing(4);
        hboxLayout1->setContentsMargins(4, 4, 4, 4);
        hboxLayout1->setObjectName(QString::fromUtf8("hboxLayout1"));
        backButton = new QPushButton(widget_2);
        backButton->setObjectName(QString::fromUtf8("backButton"));

        hboxLayout1->addWidget(backButton);

        cancelButton = new QPushButton(widget_2);
        cancelButton->setObjectName(QString::fromUtf8("cancelButton"));

        hboxLayout1->addWidget(cancelButton);

        progressBar = new QProgressBar(widget_2);
        progressBar->setObjectName(QString::fromUtf8("progressBar"));
        progressBar->setMinimumSize(QSize(100, 0));
        progressBar->setValue(0);
        progressBar->setTextVisible(false);
        progressBar->setInvertedAppearance(false);

        hboxLayout1->addWidget(progressBar);

        progressLabel = new QLabel(widget_2);
        progressLabel->setObjectName(QString::fromUtf8("progressLabel"));
        sizePolicy3.setHeightForWidth(progressLabel->sizePolicy().hasHeightForWidth());
        progressLabel->setSizePolicy(sizePolicy3);
        progressLabel->setMinimumSize(QSize(100, 0));
        progressLabel->setAlignment(Qt::AlignRight|Qt::AlignTrailing|Qt::AlignVCenter);

        hboxLayout1->addWidget(progressLabel);


        gridLayout_3->addWidget(widget_2, 1, 0, 1, 1);

        QWidget::setTabOrder(urlEdit, userEdit);
        QWidget::setTabOrder(userEdit, passwordEdit);
        QWidget::setTabOrder(passwordEdit, searchButton);
        QWidget::setTabOrder(searchButton, backButton);
        QWidget::setTabOrder(backButton, cancelButton);
        QWidget::setTabOrder(cancelButton, autoLoadCheck);
        QWidget::setTabOrder(autoLoadCheck, buttonBox);

        retranslateUi(BisqueWebAccessDialog);

        QMetaObject::connectSlotsByName(BisqueWebAccessDialog);
    } // setupUi

    void retranslateUi(QDialog *BisqueWebAccessDialog)
    {
        BisqueWebAccessDialog->setWindowTitle(QApplication::translate("BisqueWebAccessDialog", "Bisque Access", 0, QApplication::UnicodeUTF8));
        groupBox_3->setTitle(QApplication::translate("BisqueWebAccessDialog", "Bisque server configuration", 0, QApplication::UnicodeUTF8));
        label->setText(QApplication::translate("BisqueWebAccessDialog", "Url", 0, QApplication::UnicodeUTF8));
        urlEdit->setText(QApplication::translate("BisqueWebAccessDialog", "http://dough.ece.ucsb.edu/", 0, QApplication::UnicodeUTF8));
        label_2->setText(QApplication::translate("BisqueWebAccessDialog", "User", 0, QApplication::UnicodeUTF8));
        userEdit->setText(QString());
        searchButton->setText(QApplication::translate("BisqueWebAccessDialog", "Browse", 0, QApplication::UnicodeUTF8));
        label_3->setText(QApplication::translate("BisqueWebAccessDialog", "Password", 0, QApplication::UnicodeUTF8));
        passwordEdit->setText(QString());
        pathLabel->setText(QString());
        autoLoadCheck->setText(QApplication::translate("BisqueWebAccessDialog", "Auto load", 0, QApplication::UnicodeUTF8));
        groupBox->setTitle(QApplication::translate("BisqueWebAccessDialog", "Bisque web", 0, QApplication::UnicodeUTF8));
        backButton->setText(QApplication::translate("BisqueWebAccessDialog", "Back", 0, QApplication::UnicodeUTF8));
        cancelButton->setText(QApplication::translate("BisqueWebAccessDialog", "Cancel", 0, QApplication::UnicodeUTF8));
        progressBar->setFormat(QApplication::translate("BisqueWebAccessDialog", "%p%", 0, QApplication::UnicodeUTF8));
        progressLabel->setText(QApplication::translate("BisqueWebAccessDialog", "URL", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class BisqueWebAccessDialog: public Ui_BisqueWebAccessDialog {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_BISQUEWEBACCESS_H

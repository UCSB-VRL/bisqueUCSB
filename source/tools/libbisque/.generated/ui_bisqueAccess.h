/********************************************************************************
** Form generated from reading UI file 'bisqueAccess.ui'
**
** Created: Fri Jun 21 14:56:03 2013
**      by: Qt User Interface Compiler version 4.8.4
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_BISQUEACCESS_H
#define UI_BISQUEACCESS_H

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
#include <QtGui/QListWidget>
#include <QtGui/QProgressBar>
#include <QtGui/QPushButton>
#include <QtGui/QTableWidget>
#include <QtGui/QWidget>

QT_BEGIN_NAMESPACE

class Ui_BisqueAccessDialog
{
public:
    QGridLayout *gridLayout;
    QGroupBox *groupBox_3;
    QGridLayout *gridLayout1;
    QLabel *label;
    QLineEdit *urlEdit;
    QLabel *label_2;
    QLineEdit *userEdit;
    QLabel *statusLabel;
    QLabel *label_3;
    QLineEdit *passwordEdit;
    QGroupBox *groupBox_2;
    QGridLayout *gridLayout2;
    QLineEdit *searchEdit;
    QPushButton *searchButton;
    QGroupBox *groupBox;
    QGridLayout *gridLayout3;
    QListWidget *imagesListWidget;
    QLabel *imageLabel;
    QCheckBox *showTagsCheck;
    QTableWidget *TagsTableWidget;
    QLabel *fileNameLabel;
    QWidget *widget_2;
    QHBoxLayout *hboxLayout;
    QPushButton *cancelButton;
    QProgressBar *progressBar;
    QLabel *progressLabel;
    QWidget *widget;
    QHBoxLayout *hboxLayout1;
    QLabel *pathLabel;
    QPushButton *downloadButton;
    QDialogButtonBox *buttonBox;

    void setupUi(QDialog *BisqueAccessDialog)
    {
        if (BisqueAccessDialog->objectName().isEmpty())
            BisqueAccessDialog->setObjectName(QString::fromUtf8("BisqueAccessDialog"));
        BisqueAccessDialog->resize(616, 672);
        gridLayout = new QGridLayout(BisqueAccessDialog);
        gridLayout->setObjectName(QString::fromUtf8("gridLayout"));
        groupBox_3 = new QGroupBox(BisqueAccessDialog);
        groupBox_3->setObjectName(QString::fromUtf8("groupBox_3"));
        gridLayout1 = new QGridLayout(groupBox_3);
        gridLayout1->setObjectName(QString::fromUtf8("gridLayout1"));
        label = new QLabel(groupBox_3);
        label->setObjectName(QString::fromUtf8("label"));
        QSizePolicy sizePolicy(QSizePolicy::Maximum, QSizePolicy::Preferred);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(label->sizePolicy().hasHeightForWidth());
        label->setSizePolicy(sizePolicy);

        gridLayout1->addWidget(label, 0, 0, 1, 1);

        urlEdit = new QLineEdit(groupBox_3);
        urlEdit->setObjectName(QString::fromUtf8("urlEdit"));

        gridLayout1->addWidget(urlEdit, 0, 1, 1, 2);

        label_2 = new QLabel(groupBox_3);
        label_2->setObjectName(QString::fromUtf8("label_2"));
        sizePolicy.setHeightForWidth(label_2->sizePolicy().hasHeightForWidth());
        label_2->setSizePolicy(sizePolicy);

        gridLayout1->addWidget(label_2, 1, 0, 1, 1);

        userEdit = new QLineEdit(groupBox_3);
        userEdit->setObjectName(QString::fromUtf8("userEdit"));
        userEdit->setMaximumSize(QSize(300, 16777215));

        gridLayout1->addWidget(userEdit, 1, 1, 1, 1);

        statusLabel = new QLabel(groupBox_3);
        statusLabel->setObjectName(QString::fromUtf8("statusLabel"));
        QSizePolicy sizePolicy1(QSizePolicy::Expanding, QSizePolicy::Preferred);
        sizePolicy1.setHorizontalStretch(0);
        sizePolicy1.setVerticalStretch(0);
        sizePolicy1.setHeightForWidth(statusLabel->sizePolicy().hasHeightForWidth());
        statusLabel->setSizePolicy(sizePolicy1);
        statusLabel->setTextFormat(Qt::RichText);
        statusLabel->setAlignment(Qt::AlignCenter);

        gridLayout1->addWidget(statusLabel, 1, 2, 2, 1);

        label_3 = new QLabel(groupBox_3);
        label_3->setObjectName(QString::fromUtf8("label_3"));
        sizePolicy.setHeightForWidth(label_3->sizePolicy().hasHeightForWidth());
        label_3->setSizePolicy(sizePolicy);

        gridLayout1->addWidget(label_3, 2, 0, 1, 1);

        passwordEdit = new QLineEdit(groupBox_3);
        passwordEdit->setObjectName(QString::fromUtf8("passwordEdit"));
        passwordEdit->setMaximumSize(QSize(300, 16777215));
        passwordEdit->setEchoMode(QLineEdit::Password);

        gridLayout1->addWidget(passwordEdit, 2, 1, 1, 1);


        gridLayout->addWidget(groupBox_3, 0, 0, 1, 1);

        groupBox_2 = new QGroupBox(BisqueAccessDialog);
        groupBox_2->setObjectName(QString::fromUtf8("groupBox_2"));
        gridLayout2 = new QGridLayout(groupBox_2);
        gridLayout2->setObjectName(QString::fromUtf8("gridLayout2"));
        searchEdit = new QLineEdit(groupBox_2);
        searchEdit->setObjectName(QString::fromUtf8("searchEdit"));

        gridLayout2->addWidget(searchEdit, 0, 0, 1, 1);

        searchButton = new QPushButton(groupBox_2);
        searchButton->setObjectName(QString::fromUtf8("searchButton"));

        gridLayout2->addWidget(searchButton, 0, 1, 1, 1);


        gridLayout->addWidget(groupBox_2, 1, 0, 1, 1);

        groupBox = new QGroupBox(BisqueAccessDialog);
        groupBox->setObjectName(QString::fromUtf8("groupBox"));
        gridLayout3 = new QGridLayout(groupBox);
        gridLayout3->setObjectName(QString::fromUtf8("gridLayout3"));
        imagesListWidget = new QListWidget(groupBox);
        imagesListWidget->setObjectName(QString::fromUtf8("imagesListWidget"));
        imagesListWidget->setMaximumSize(QSize(16777215, 16777215));

        gridLayout3->addWidget(imagesListWidget, 0, 0, 4, 1);

        imageLabel = new QLabel(groupBox);
        imageLabel->setObjectName(QString::fromUtf8("imageLabel"));
        imageLabel->setMinimumSize(QSize(200, 200));
        imageLabel->setMaximumSize(QSize(16777215, 16777215));
        imageLabel->setScaledContents(false);
        imageLabel->setAlignment(Qt::AlignCenter);

        gridLayout3->addWidget(imageLabel, 0, 1, 1, 1);

        showTagsCheck = new QCheckBox(groupBox);
        showTagsCheck->setObjectName(QString::fromUtf8("showTagsCheck"));
        showTagsCheck->setChecked(true);

        gridLayout3->addWidget(showTagsCheck, 2, 1, 1, 1);

        TagsTableWidget = new QTableWidget(groupBox);
        if (TagsTableWidget->columnCount() < 2)
            TagsTableWidget->setColumnCount(2);
        QTableWidgetItem *__qtablewidgetitem = new QTableWidgetItem();
        TagsTableWidget->setHorizontalHeaderItem(0, __qtablewidgetitem);
        QTableWidgetItem *__qtablewidgetitem1 = new QTableWidgetItem();
        TagsTableWidget->setHorizontalHeaderItem(1, __qtablewidgetitem1);
        TagsTableWidget->setObjectName(QString::fromUtf8("TagsTableWidget"));

        gridLayout3->addWidget(TagsTableWidget, 3, 1, 1, 1);

        fileNameLabel = new QLabel(groupBox);
        fileNameLabel->setObjectName(QString::fromUtf8("fileNameLabel"));
        fileNameLabel->setAlignment(Qt::AlignCenter);

        gridLayout3->addWidget(fileNameLabel, 1, 1, 1, 1);


        gridLayout->addWidget(groupBox, 2, 0, 1, 1);

        widget_2 = new QWidget(BisqueAccessDialog);
        widget_2->setObjectName(QString::fromUtf8("widget_2"));
        hboxLayout = new QHBoxLayout(widget_2);
        hboxLayout->setObjectName(QString::fromUtf8("hboxLayout"));
        cancelButton = new QPushButton(widget_2);
        cancelButton->setObjectName(QString::fromUtf8("cancelButton"));

        hboxLayout->addWidget(cancelButton);

        progressBar = new QProgressBar(widget_2);
        progressBar->setObjectName(QString::fromUtf8("progressBar"));
        progressBar->setMinimumSize(QSize(100, 0));
        progressBar->setValue(0);

        hboxLayout->addWidget(progressBar);

        progressLabel = new QLabel(widget_2);
        progressLabel->setObjectName(QString::fromUtf8("progressLabel"));
        progressLabel->setMinimumSize(QSize(100, 0));

        hboxLayout->addWidget(progressLabel);


        gridLayout->addWidget(widget_2, 3, 0, 1, 1);

        widget = new QWidget(BisqueAccessDialog);
        widget->setObjectName(QString::fromUtf8("widget"));
        hboxLayout1 = new QHBoxLayout(widget);
        hboxLayout1->setObjectName(QString::fromUtf8("hboxLayout1"));
        pathLabel = new QLabel(widget);
        pathLabel->setObjectName(QString::fromUtf8("pathLabel"));
        sizePolicy1.setHeightForWidth(pathLabel->sizePolicy().hasHeightForWidth());
        pathLabel->setSizePolicy(sizePolicy1);
        pathLabel->setCursor(QCursor(Qt::PointingHandCursor));
        pathLabel->setTextFormat(Qt::RichText);

        hboxLayout1->addWidget(pathLabel);

        downloadButton = new QPushButton(widget);
        downloadButton->setObjectName(QString::fromUtf8("downloadButton"));
        downloadButton->setEnabled(true);

        hboxLayout1->addWidget(downloadButton);

        buttonBox = new QDialogButtonBox(widget);
        buttonBox->setObjectName(QString::fromUtf8("buttonBox"));
        QSizePolicy sizePolicy2(QSizePolicy::Maximum, QSizePolicy::Fixed);
        sizePolicy2.setHorizontalStretch(0);
        sizePolicy2.setVerticalStretch(0);
        sizePolicy2.setHeightForWidth(buttonBox->sizePolicy().hasHeightForWidth());
        buttonBox->setSizePolicy(sizePolicy2);
        buttonBox->setOrientation(Qt::Horizontal);
        buttonBox->setStandardButtons(QDialogButtonBox::Close|QDialogButtonBox::Open);

        hboxLayout1->addWidget(buttonBox);


        gridLayout->addWidget(widget, 4, 0, 1, 1);


        retranslateUi(BisqueAccessDialog);

        QMetaObject::connectSlotsByName(BisqueAccessDialog);
    } // setupUi

    void retranslateUi(QDialog *BisqueAccessDialog)
    {
        BisqueAccessDialog->setWindowTitle(QApplication::translate("BisqueAccessDialog", "Bisque Access", 0, QApplication::UnicodeUTF8));
        groupBox_3->setTitle(QApplication::translate("BisqueAccessDialog", "Bisque server configuration", 0, QApplication::UnicodeUTF8));
        label->setText(QApplication::translate("BisqueAccessDialog", "Url", 0, QApplication::UnicodeUTF8));
        urlEdit->setText(QApplication::translate("BisqueAccessDialog", "http://dough.ece.ucsb.edu/", 0, QApplication::UnicodeUTF8));
        label_2->setText(QApplication::translate("BisqueAccessDialog", "User", 0, QApplication::UnicodeUTF8));
        userEdit->setText(QString());
        statusLabel->setText(QString());
        label_3->setText(QApplication::translate("BisqueAccessDialog", "Password", 0, QApplication::UnicodeUTF8));
        passwordEdit->setText(QString());
        groupBox_2->setTitle(QApplication::translate("BisqueAccessDialog", "Search", 0, QApplication::UnicodeUTF8));
        searchButton->setText(QApplication::translate("BisqueAccessDialog", "Search", 0, QApplication::UnicodeUTF8));
        groupBox->setTitle(QApplication::translate("BisqueAccessDialog", "Images", 0, QApplication::UnicodeUTF8));
        imageLabel->setText(QString());
        showTagsCheck->setText(QApplication::translate("BisqueAccessDialog", "Show tags", 0, QApplication::UnicodeUTF8));
        QTableWidgetItem *___qtablewidgetitem = TagsTableWidget->horizontalHeaderItem(0);
        ___qtablewidgetitem->setText(QApplication::translate("BisqueAccessDialog", "Tag", 0, QApplication::UnicodeUTF8));
        QTableWidgetItem *___qtablewidgetitem1 = TagsTableWidget->horizontalHeaderItem(1);
        ___qtablewidgetitem1->setText(QApplication::translate("BisqueAccessDialog", "Value", 0, QApplication::UnicodeUTF8));
        fileNameLabel->setText(QString());
        cancelButton->setText(QApplication::translate("BisqueAccessDialog", "Cancel", 0, QApplication::UnicodeUTF8));
        progressBar->setFormat(QApplication::translate("BisqueAccessDialog", "%p%", 0, QApplication::UnicodeUTF8));
        progressLabel->setText(QString());
        pathLabel->setText(QString());
        downloadButton->setText(QApplication::translate("BisqueAccessDialog", "Download", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class BisqueAccessDialog: public Ui_BisqueAccessDialog {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_BISQUEACCESS_H

Ext.define('Bisque.ResourceBrowser.viewStateManager', {
    //	ResourceBrowser view-state
    constructor : function(mode) {
        this.cBar = {
            cbar : false,

            searchBar : false,

            btnActivate : false,
            btnTS : false,
            btnRefresh : false,

            btnLayoutThumb : false,
            btnLayoutCard : false,
            btnLayoutGrid : false,
            btnLayoutFull : false,

            btnLayoutLeft : false,
            btnLayoutRight : false,

            slider : false,

            btnGear : false,
            btnOrganizer : false,
            btnDataset : false,
            btnLink : false,
            btnPreferences : false
        };

        switch(mode) {
            case 'MexBrowser':
            case 'ViewerOnly': {
                this.cBar.btnActivate = true;
                this.cBar.btnRefresh = false; // true
                this.cBar.btnRefresh_only_update = true;

                this.cBar.searchBar = true;

                this.cBar.btnLayoutThumb = true;
                this.cBar.btnLayoutCard = true;
                this.cBar.btnLayoutGrid = true;
                this.cBar.btnLayoutFull = true;

                //this.cBar.btnGear = false;

                break;
            }
            case 'DatasetBrowser': {
                this.cBar.searchBar = true;

                this.cBar.btnLayoutThumb = true;
                this.cBar.btnLayoutCard = true;
                this.cBar.btnLayoutGrid = true;
                this.cBar.btnLayoutFull = true;

                //this.cBar.btnGear = false;
                break;
            }
            case 'ViewSearch': {
                this.cBar.btnActivate = true;
                this.cBar.btnTS = true;
                this.cBar.btnRefresh = true;

                this.cBar.btnLayoutThumb = true;
                this.cBar.btnLayoutCard = true;
                this.cBar.btnLayoutGrid = true;
                this.cBar.btnLayoutFull = true;

                this.cBar.slider = true;
                //this.cBar.btnGear = false;

                break;
            }
            case 'ViewerLayouts': {
                //this.cBar.searchBar = false;
                //this.cBar.btnGear = false;
                break;
            }
            case 'ModuleBrowser': {
                this.cBar.cbar = true;
                break;
            }
        }

        return this;
    }
});

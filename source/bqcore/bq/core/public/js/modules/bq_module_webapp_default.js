/*******************************************************************************

  webapp - a fully integrated interface for a module

  This algorithm takes user clicks as inputs and tracks the apex of an organ
  and reports out the tip angle of the apex. Initially the tip is located with
  a user click and is subsequently tracked using a corner detector in
  combination with a nearest neighbor tracking approach.

*******************************************************************************/

function WebApp (args) {
    this.module_url = location.pathname;
    this.label_run = "Run";
    BQWebApp.call(this, args);
}
WebApp.prototype = new BQWebApp();
WebApp.prototype.constructor = WebApp;

WebApp.prototype.run = function () {
    BQWebApp.prototype.run.call(this);
};
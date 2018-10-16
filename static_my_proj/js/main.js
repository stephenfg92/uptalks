var serviceWorkerPath = "/service-worker.js";
var charchaServiceWorker = registerServiceWorker(serviceWorkerPath);
function registerServiceWorker(serviceWorkerPath){
  if('serviceWorker' in navigator){
    navigator.serviceWorker
      .register(serviceWorkerPath, {updateViaCache: 'all'})
        .then(
          function(reg){
            console.log('service worker registered');
          }
        ).catch(function(error){
          console.log(error)
        });
  }
}
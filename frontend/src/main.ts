import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(() => {
  document.body.innerHTML = 'No fue posible iniciar la aplicación.';
});

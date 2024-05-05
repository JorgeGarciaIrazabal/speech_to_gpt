import { enableProdMode, SecurityContext } from '@angular/core';
import { bootstrapApplication } from '@angular/platform-browser';
import { RouteReuseStrategy, provideRouter } from '@angular/router';
import { IonicRouteStrategy, provideIonicAngular } from '@ionic/angular/standalone';

import { routes } from './app/app.routes';
import { AppComponent } from './app/app.component';
import { environment } from './environments/environment';
import {MarkdownService, SECURITY_CONTEXT} from "ngx-markdown";

if (environment.production) {
  enableProdMode();
}

bootstrapApplication(AppComponent, {
  providers: [
    { provide: RouteReuseStrategy, useClass: IonicRouteStrategy },
    MarkdownService,
    { provide: SECURITY_CONTEXT, useValue: SecurityContext.NONE },
    provideIonicAngular(),
    provideRouter(routes),
  ],
});

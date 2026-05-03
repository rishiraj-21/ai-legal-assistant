import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';
import { ToastService } from '../services/toast.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const toast = inject(ToastService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 429) {
        toast.error('Too many requests', 'Please wait a moment before trying again.');
      } else if (error.status === 0) {
        toast.error('Network error', 'Could not reach the server. Check your connection.');
      } else if (error.status >= 500) {
        const correlationId = error.headers?.get('X-Correlation-Id');
        const detail = correlationId ? `Reference: ${correlationId}` : 'Please try again later.';
        toast.error('Server error', detail);
      }
      return throwError(() => error);
    })
  );
};

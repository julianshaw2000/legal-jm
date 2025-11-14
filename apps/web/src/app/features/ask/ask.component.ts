import {
  ChangeDetectionStrategy,
  Component,
  WritableSignal,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormControl, Validators } from '@angular/forms';
import { MaterialModule } from '../../shared/material.module';

@Component({
  standalone: true,
  selector: 'app-ask',
  imports: [CommonModule, ReactiveFormsModule, MaterialModule],
  template: `
    <div class="pad">
      <h2>Ask</h2>
      <form (ngSubmit)="submit()">
        <mat-form-field appearance="outline" class="full">
          <mat-label>Your question</mat-label>
          <input matInput [formControl]="q" />
        </mat-form-field>
        <button
          mat-raised-button
          color="primary"
          type="submit"
          [disabled]="q.invalid"
        >
          Ask
        </button>
      </form>

      @if (answer(); as a) {
      <div class="answer">
        <h3>Answer</h3>
        <p>{{ a }}</p>
      </div>
      }
    </div>
  `,
  styles: [
    `
      .pad {
        padding: 1rem;
        max-width: 800px;
        margin: 0 auto;
      }
      .full {
        width: 100%;
      }
      .answer {
        margin-top: 1rem;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AskComponent {
  q = new FormControl<string>('', {
    nonNullable: true,
    validators: [Validators.required],
  });
  answer: WritableSignal<string | null> = signal(null);

  submit(): void {
    if (this.q.invalid) return;
    // Placeholder; will call API later
    this.answer.set('This is a placeholder answer (dry run).');
  }
}

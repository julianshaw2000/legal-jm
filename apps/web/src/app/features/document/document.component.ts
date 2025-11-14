import {
  ChangeDetectionStrategy,
  Component,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';

@Component({
  standalone: true,
  selector: 'app-document',
  imports: [CommonModule],
  template: `
    <div class="pad">
      <h2>Document {{ id() }}</h2>
      <p>Document details and sections.</p>
    </div>
  `,
  styles: [
    `
      .pad {
        padding: 1rem;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DocumentComponent {
  private route = inject(ActivatedRoute);
  readonly id = signal<string | null>(null);

  constructor() {
    this.id.set(this.route.snapshot.paramMap.get('id'));
  }
}

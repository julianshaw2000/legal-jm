import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../shared/material.module';

@Component({
  standalone: true,
  selector: 'app-browse',
  imports: [CommonModule, MaterialModule],
  template: `
    <div class="pad">
      <h2>Browse</h2>
      <p>List of documents will appear here.</p>
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
export class BrowseComponent {}



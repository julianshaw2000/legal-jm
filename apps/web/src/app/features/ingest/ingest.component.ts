import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../shared/material.module';

@Component({
  standalone: true,
  selector: 'app-ingest',
  imports: [CommonModule, MaterialModule],
  template: `
    <div class="pad">
      <h2>Ingest</h2>
      <p>Upload or trigger ingestion jobs here.</p>
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
export class IngestComponent {}



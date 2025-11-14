import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../shared/material.module';

@Component({
  standalone: true,
  selector: 'app-admin-users',
  imports: [CommonModule, MaterialModule],
  template: `
    <div class="pad">
      <h2>Admin: Users</h2>
      <p>User management will appear here.</p>
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
export class AdminUsersComponent {}



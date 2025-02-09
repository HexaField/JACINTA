// src/types.ts
export interface Task {
  id: string
  title: string
  description?: string
  status: 'not-started' | 'in-progress' | 'completed'
}

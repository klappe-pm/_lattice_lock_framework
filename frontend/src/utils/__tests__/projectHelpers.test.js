import { describe, it, expect } from 'vitest';
import { 
  generateId, 
  formatDate, 
  formatDateTime, 
  validateProject, 
  searchProjects, 
  sortProjects, 
  filterByTags, 
  getAllTags,
  truncateText,
  getRandomColor,
  exportProject,
  importProject
} from '../projectHelpers';

describe('projectHelpers', () => {
  describe('generateId', () => {
    it('should generate unique IDs', () => {
      const id1 = generateId();
      const id2 = generateId();
      expect(id1).not.toBe(id2);
      expect(typeof id1).toBe('string');
    });
  });

  describe('formatDate', () => {
    it('should format recent dates correctly', () => {
      const now = Date.now();
      expect(formatDate(now)).toBe('Just now');
      expect(formatDate(now - 120000)).toBe('2 minutes ago'); // Use 2 mins to be safe
    });

    it('should format older dates', () => {
        const date = new Date('2023-01-15'); // Mid-month to avoid timezone shift
        expect(formatDate(date)).toContain('Jan');
    });
  });
  
  describe('formatDateTime', () => {
      it('should format date and time', () => {
          const date = new Date('2023-01-01T12:00:00');
          const formatted = formatDateTime(date);
          expect(formatted).toContain('2023');
          expect(formatted).toContain('12:00');
      });
  });

  describe('validateProject', () => {
    it('should validate correct project', () => {
      const project = { name: 'Test', description: 'Desc', color: '#000000' };
      const { isValid, errors } = validateProject(project);
      expect(isValid).toBe(true);
      expect(errors).toHaveLength(0);
    });

    it('should invalidate missing name', () => {
      const project = { name: '' };
      const { isValid, errors } = validateProject(project);
      expect(isValid).toBe(false);
      expect(errors).toContain('Project name is required');
    });
    
    it('should invalidate invalid color', () => {
        const project = { name: 'Test', color: 'invalid' };
        const { isValid, errors } = validateProject(project);
        expect(isValid).toBe(false);
        expect(errors).toContain('Color must be a valid hex color code');
    });
  });

  describe('searchProjects', () => {
    const projects = [
      { name: 'Alpha', description: 'First project', tags: ['red'] },
      { name: 'Beta', description: 'Second project', tags: ['blue'] }
    ];

    it('should find by name', () => {
      const results = searchProjects(projects, 'Alpha');
      expect(results).toHaveLength(1);
      expect(results[0].name).toBe('Alpha');
    });

    it('should find by tag', () => {
      const results = searchProjects(projects, 'red');
      expect(results).toHaveLength(1);
      expect(results[0].name).toBe('Alpha');
    });
  });
  
  describe('sortProjects', () => {
      const projects = [
          { name: 'B', updatedAt: 100 },
          { name: 'A', updatedAt: 200 }
      ];
      
      it('should sort by name asc', () => {
          const sorted = sortProjects(projects, 'name', 'asc');
          expect(sorted[0].name).toBe('A');
      });
      
      it('should sort by updatedAt desc', () => {
          const sorted = sortProjects(projects, 'updatedAt', 'desc');
          expect(sorted[0].name).toBe('A');
      });
  });
  
  describe('filterByTags', () => {
      const projects = [
          { tags: ['a'] },
          { tags: ['b'] },
          { tags: ['a', 'b'] }
      ];
      
      it('should filter by single tag', () => {
          const results = filterByTags(projects, ['a']);
          expect(results).toHaveLength(2);
      });
  });

  describe('getAllTags', () => {
    it('should collect unique tags', () => {
      const projects = [{ tags: ['a', 'b'] }, { tags: ['b', 'c'] }];
      const tags = getAllTags(projects);
      expect(tags).toEqual(['a', 'b', 'c']);
    });
    
    it('should handle undefined tags', () => {
        const projects = [{}];
        const tags = getAllTags(projects);
        expect(tags).toEqual([]);
    });
  });
  
    describe('truncateText', () => {
        it('should truncate long text', () => {
            expect(truncateText('hello world', 5)).toBe('hello...');
        });
        
        it('should return short text as is', () => {
            expect(truncateText('hi', 5)).toBe('hi');
        });
    });
    
    describe('getRandomColor', () => {
        it('should return a string', () => {
            expect(typeof getRandomColor()).toBe('string');
        });
    });
    
    describe('import/export', () => {
        it('should export and import correctly', () => {
            const project = { name: 'Test' };
            const json = exportProject(project);
            const result = importProject(json);
            expect(result.success).toBe(true);
            expect(result.project.name).toBe('Test');
            expect(result.project.id).toBeDefined();
        });
        
        it('should handle invalid json import', () => {
            const result = importProject('invalid');
            expect(result.success).toBe(false);
        });
    });
});

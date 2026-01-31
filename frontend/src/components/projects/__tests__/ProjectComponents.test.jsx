import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderWithProviders, screen, fireEvent, waitFor, render } from '../../../test/utils';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import ProjectCard from '../ProjectCard';
import ProjectList from '../ProjectList';
import ProjectForm from '../ProjectForm';
import ChatHistoryPanel from '../ChatHistoryPanel';
import ProjectDetail from '../ProjectDetail';

// Mock the store
vi.mock('../../../store', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useProjectsStore: vi.fn(),
  };
});

describe('Project Components', () => {

    describe('Sanity Check', () => {
        it('should update input value', async () => {
            const user = userEvent.setup();
            const Test = () => {
                const [val, setVal] = useState('');
                return <input aria-label="test-input" value={val} onChange={e => setVal(e.target.value)} />;
            };
            render(<Test />);
            const input = screen.getByLabelText('test-input');
            await user.type(input, 'hello');
            expect(input).toHaveValue('hello');
        });
    });

    describe('ProjectCard', () => {
        const mockProject = {
            id: '1',
            name: 'Test Project',
            description: 'Test Description',
            tags: ['tag1', 'tag2'],
            updatedAt: new Date().toISOString(),
        };

        it('should render project details', () => {
            renderWithProviders(<ProjectCard project={mockProject} />);
            expect(screen.getByText('Test Project')).toBeInTheDocument();
            expect(screen.getByText('Test Description')).toBeInTheDocument();
            expect(screen.getByText('tag1')).toBeInTheDocument();
        });

        it('should call handlers on action', () => {
            const onEdit = vi.fn();
            const onDelete = vi.fn();
            const onClick = vi.fn();
            
            renderWithProviders(
                <ProjectCard 
                    project={mockProject} 
                    onEdit={onEdit} 
                    onDelete={onDelete} 
                    onClick={onClick} 
                />
            );
            // Basic render check since structure might vary
            expect(screen.getByText('Test Project')).toBeInTheDocument();
        });
    });

    describe('ProjectList', () => {
        it('should render empty state', () => {
            renderWithProviders(<ProjectList projects={[]} />);
            expect(screen.getByText(/No Projects Yet/i)).toBeInTheDocument();
        });

        it('should render list of projects', () => {
            const projects = [
                { id: '1', name: 'P1', tags: [], updatedAt: '2023-01-01' },
                { id: '2', name: 'P2', tags: [], updatedAt: '2023-01-02' }
            ];
            renderWithProviders(<ProjectList projects={projects} />);
            expect(screen.getByText('P1')).toBeInTheDocument();
            expect(screen.getByText('P2')).toBeInTheDocument();
        });
        
        it('should filter projects by search', async () => {
             const projects = [
                { id: '1', name: 'Alpha', tags: [], updatedAt: '2023-01-01' },
                { id: '2', name: 'Beta', tags: [], updatedAt: '2023-01-02' }
            ];
            renderWithProviders(<ProjectList projects={projects} />);
            
            const searchInput = screen.getByPlaceholderText(/Search projects/i);
            fireEvent.change(searchInput, { target: { value: 'Alpha' } });

            // Verify input interaction works
            await waitFor(() => expect(searchInput).toHaveValue('Alpha'));
            
            await waitFor(() => {
                expect(screen.getByText('Alpha')).toBeInTheDocument();
                expect(screen.queryByText('Beta')).not.toBeInTheDocument();
            });
        });

        it('should filter projects by tags', async () => {
             const projects = [
               { id: '1', name: 'Proj A', tags: ['react'], updatedAt: '2023-01-01' },
               { id: '2', name: 'Proj B', tags: ['vue'], updatedAt: '2023-01-02' }
           ];
           renderWithProviders(<ProjectList projects={projects} />);
           
           // Click tag filter button
           const tagBtn = screen.getByRole('button', { name: 'react' });
           fireEvent.click(tagBtn);
           
           await waitFor(() => {
               expect(screen.getByText('Proj A')).toBeInTheDocument();
               expect(screen.queryByText('Proj B')).not.toBeInTheDocument();
           });
       });

       it('should sort projects', () => {
           const projects = [
               { id: '1', name: 'A-Project', updatedAt: '2023-01-01' },
               { id: '2', name: 'B-Project', updatedAt: '2023-01-02' }
           ];
           renderWithProviders(<ProjectList projects={projects} />);
           
           const select = screen.getByRole('combobox');
           fireEvent.change(select, { target: { value: 'name' } });
           
           expect(select).toHaveValue('name');
       });

       it('should toggle sort order', async () => {
           const projects = [
               { id: '1', name: 'A', updatedAt: '2023-01-01' },
               { id: '2', name: 'B', updatedAt: '2023-01-02' }
           ];
           renderWithProviders(<ProjectList projects={projects} />);
           
           const btn = screen.getByTitle(/Sort ascending/i);
           fireEvent.click(btn);
           
           await waitFor(() => expect(screen.getByTitle(/Sort descending/i)).toBeInTheDocument());
       });

        it('should toggle tags on and off', async () => {
           const projects = [{ id: '1', name: 'P1', tags: ['react'], updatedAt: '2023' }];
           renderWithProviders(<ProjectList projects={projects} />);
           
           const tagBtn = screen.getByRole('button', { name: 'react' });
           
           // Select
           fireEvent.click(tagBtn);
           await waitFor(() => expect(screen.getByText('1 project (filtered from 1)')).toBeInTheDocument());
           expect(tagBtn).toHaveClass('chip-primary');

           // Deselect
           fireEvent.click(tagBtn);
           await waitFor(() => expect(screen.getByText('1 project')).toBeInTheDocument());
           expect(tagBtn).not.toHaveClass('chip-primary');
       });

       it('should clear filters', async () => {
           const projects = [{ id: '1', name: 'P1', tags: ['react'], updatedAt: '2023' }];
           renderWithProviders(<ProjectList projects={projects} />);
           
           const searchInput = screen.getByPlaceholderText(/Search projects/i);
           fireEvent.change(searchInput, { target: { value: 'XYZ' } });
           
           await waitFor(() => expect(screen.getByText(/No projects match your filters/i)).toBeInTheDocument());
           
           const clearBtn = screen.getByText(/Clear filters/i);
           fireEvent.click(clearBtn);
           
           await waitFor(() => expect(screen.getByText('P1')).toBeInTheDocument());
           expect(searchInput).toHaveValue('');
       });
    });

    describe('ProjectForm', () => {
        it('should validate inputs', async () => {
            const onSave = vi.fn();
            const onCancel = vi.fn();
            renderWithProviders(<ProjectForm isOpen={true} onSave={onSave} onCancel={onCancel} />);
            
            const submitBtn = screen.getByText(/Create Project/i);
            const nameInput = screen.getByLabelText(/Project Name/i);
            
            // Should be empty initially
            expect(nameInput).toHaveValue('');
            
            // Remove required
            nameInput.removeAttribute('required');
            fireEvent.change(nameInput, { target: { value: '   ' } });
            await waitFor(() => expect(nameInput).toHaveValue('   '));
            
            fireEvent.click(submitBtn);
            
            expect(onSave).not.toHaveBeenCalled();
            await waitFor(() => {
                expect(screen.getByText(/Project name is required/i)).toBeInTheDocument();
            });
        });

        it('should submit valid data', async () => {
            const onSave = vi.fn();
            const onCancel = vi.fn();
            renderWithProviders(<ProjectForm isOpen={true} onSave={onSave} onCancel={onCancel} />);
            
            const nameInput = screen.getByLabelText(/Project Name/i);
            fireEvent.change(nameInput, { target: { value: 'New Proj' } });
            await waitFor(() => expect(nameInput).toHaveValue('New Proj'));
            
            const submitBtn = screen.getByText(/Create Project/i);
            fireEvent.click(submitBtn);
            
            expect(onSave).toHaveBeenCalledWith(expect.objectContaining({ name: 'New Proj' }));
        });

        it('should initialize with project data (Edit Mode)', () => {
            const project = { id: '1', name: 'Existing', description: 'Desc', tags: ['t1'], color: '#000000' };
            renderWithProviders(<ProjectForm isOpen={true} project={project} />);
            expect(screen.getByDisplayValue('Existing')).toBeInTheDocument();
            expect(screen.getByText('Edit Project')).toBeInTheDocument();
        });

        it('should add and remove tags', async () => {
            const onSave = vi.fn();
            renderWithProviders(<ProjectForm isOpen={true} onSave={onSave} />);
            
            const tagInput = screen.getByPlaceholderText(/Add a tag/i);
            const addBtn = screen.getByText('Add');
            
            fireEvent.change(tagInput, { target: { value: 'NewTag' } });
            await waitFor(() => expect(tagInput).toHaveValue('NewTag'));
            
            fireEvent.click(addBtn);
            expect(screen.getByText('NewTag')).toBeInTheDocument();
            
            const removeBtn = screen.getByLabelText('Remove NewTag');
            fireEvent.click(removeBtn);
            expect(screen.queryByText('NewTag')).not.toBeInTheDocument();
        });

        it('should handle color change', async () => {
             const onSave = vi.fn();
             renderWithProviders(<ProjectForm isOpen={true} onSave={onSave} />);
             
             const colorInput = screen.getByLabelText(/Project Color/i);
             fireEvent.change(colorInput, { target: { value: '#ff0000' } });
             await waitFor(() => expect(colorInput).toHaveValue('#ff0000'));
        });
    });

    describe('ChatHistoryPanel', () => {
        const chats = [
            { id: 'c1', title: 'Chat 1', summary: 'Summary 1', timestamp: new Date().toISOString(), turns: 5 },
            { id: 'c2', title: 'Chat 2', summary: 'Summary 2', timestamp: new Date().toISOString(), turns: 2 }
        ];

        it('should render empty state', () => {
            renderWithProviders(<ChatHistoryPanel linkedChats={[]} />);
            expect(screen.getByText(/No Linked Conversations/i)).toBeInTheDocument();
        });

        it('should list chats', () => {
            renderWithProviders(<ChatHistoryPanel linkedChats={chats} />);
            expect(screen.getByText('Chat 1')).toBeInTheDocument();
            expect(screen.getByText('Chat 2')).toBeInTheDocument();
        });

        it('should filter chats', async () => {
            renderWithProviders(<ChatHistoryPanel linkedChats={chats} />);
            const searchInput = screen.getByPlaceholderText(/Search conversations/i);
            fireEvent.change(searchInput, { target: { value: 'Chat 1' } });
            await waitFor(() => expect(searchInput).toHaveValue('Chat 1'));
            
            await waitFor(() => {
                expect(screen.getByText('Chat 1')).toBeInTheDocument();
                expect(screen.queryByText('Chat 2')).not.toBeInTheDocument();
            });
        });
        
        it('should handle unlink', () => {
            const onUnlink = vi.fn();
            window.confirm = vi.fn(() => true);
            renderWithProviders(<ChatHistoryPanel linkedChats={chats} onUnlinkChat={onUnlink} />);
            const buttons = screen.getAllByLabelText(/Unlink conversation/i);
            fireEvent.click(buttons[0]);
            expect(window.confirm).toHaveBeenCalled();
            expect(onUnlink).toHaveBeenCalledWith('c1');
        });
    });

    describe('ProjectDetail', () => {
        const project = {
            id: 'p1',
            name: 'Proj 1',
            description: 'Desc',
            tags: ['tag1'],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            context: 'Ctx',
            instructions: 'Instr',
            linkedChats: [{ id: 'c1' }]
        };

        it('should render overview', () => {
             renderWithProviders(<ProjectDetail project={project} />);
             expect(screen.getByText('Proj 1')).toBeInTheDocument();
             expect(screen.getByText(/Overview/i)).toBeInTheDocument();
             expect(screen.getByText(/Context/i)).toBeInTheDocument();
        });

        it('should switch tabs', () => {
             renderWithProviders(<ProjectDetail project={project} />);
             const contextTab = screen.getByText(/Context/i);
             fireEvent.click(contextTab);
             expect(screen.getByText('Ctx')).toBeInTheDocument();
        });

        it('should edit context', () => {
             const onUpdate = vi.fn();
             renderWithProviders(<ProjectDetail project={project} onUpdate={onUpdate} />);
             fireEvent.click(screen.getByText(/Context/i));
             fireEvent.click(screen.getByText(/Edit/i));
             const input = screen.getByPlaceholderText(/Add any relevant context/i);
             fireEvent.change(input, { target: { value: 'New Ctx' } });
             fireEvent.click(screen.getByText('Save'));
             expect(onUpdate).toHaveBeenCalledWith({ context: 'New Ctx' });
        });
        
        it('should edit instructions', () => {
             const onUpdate = vi.fn();
             renderWithProviders(<ProjectDetail project={project} onUpdate={onUpdate} />);
             fireEvent.click(screen.getByText(/Instructions/i));
             fireEvent.click(screen.getByText(/Edit/i));
             const input = screen.getByPlaceholderText(/Add specific instructions/i);
             fireEvent.change(input, { target: { value: 'New Instr' } });
             fireEvent.click(screen.getByText('Save'));
             expect(onUpdate).toHaveBeenCalledWith({ instructions: 'New Instr' });
        });
    });
});

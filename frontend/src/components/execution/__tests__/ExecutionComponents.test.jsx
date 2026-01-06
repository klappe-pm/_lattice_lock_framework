import { describe, it, expect, vi } from 'vitest';
import { renderWithProviders, screen, userEvent } from '../../../test/utils';
import PromptInput from '../PromptInput';
import { useExecutionStore } from '../../../store';

// Mock the store hook
vi.mock('../../../store', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useExecutionStore: vi.fn(),
  };
});

describe('PromptInput', () => {
  const defaultStore = {
    systemInstructions: '',
    setSystemInstructions: vi.fn(),
    isExecuting: false,
  };

  beforeEach(() => {
    useExecutionStore.mockReturnValue(defaultStore);
  });

  it('should render input textarea', () => {
    renderWithProviders(<PromptInput />);
    expect(screen.getByPlaceholderText(/Enter your prompt/i)).toBeInTheDocument();
  });

  it('should handle text input', async () => {
    const user = userEvent.setup();
    renderWithProviders(<PromptInput />);
    
    const input = screen.getByPlaceholderText(/Enter your prompt/i);
    await user.type(input, 'Hello world');
    
    expect(input).toHaveValue('Hello world');
  });

  it('should submit prompt on button click', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(<PromptInput onSubmit={onSubmit} />);
    
    const input = screen.getByPlaceholderText(/Enter your prompt/i);
    await user.type(input, 'Test prompt');
    
    // Select by title since it has no text
    const submitBtn = screen.getByTitle(/Send/i);
    await user.click(submitBtn);
    
    expect(onSubmit).toHaveBeenCalledWith({
      prompt: 'Test prompt',
      systemInstructions: ''
    });
    expect(input).toHaveValue(''); // Should clear after submit
  });

  it('should submit on Ctrl+Enter', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(<PromptInput onSubmit={onSubmit} />);
    
    const input = screen.getByPlaceholderText(/Enter your prompt/i);
    await user.type(input, 'Test prompt{Control>}{Enter}{/Control}');
    
    expect(onSubmit).toHaveBeenCalledWith({
      prompt: 'Test prompt',
      systemInstructions: ''
    });
  });

  it('should disable input while loading', () => {
    // Mock the store return value provided by the implementation
    useExecutionStore.mockReturnValue({
      ...defaultStore,
      isExecuting: true,
    });

    renderWithProviders(<PromptInput />); // No isLoading prop needed, uses store
    expect(screen.getByPlaceholderText(/Enter your prompt/i)).toBeDisabled();
    expect(screen.getByTitle(/Send/i)).toBeDisabled();
  });
});

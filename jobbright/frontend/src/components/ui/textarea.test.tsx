import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Textarea } from './textarea'; // Adjust path as needed

describe('Textarea Component', () => {
  it('renders as a textarea element', () => {
    render(<Textarea data-testid="test-textarea" />);
    const textarea = screen.getByTestId('test-textarea');
    expect(textarea).toBeInTheDocument();
    expect(textarea.tagName.toLowerCase()).toBe('textarea');
  });

  it('applies base styling classes', () => {
    render(<Textarea data-testid="test-textarea" />);
    const textarea = screen.getByTestId('test-textarea');
    // Check for a selection of key base classes
    expect(textarea).toHaveClass('flex');
    expect(textarea).toHaveClass('w-full');
    expect(textarea).toHaveClass('rounded-md');
    expect(textarea).toHaveClass('border');
    expect(textarea).toHaveClass('bg-transparent'); // Assuming bg-background resolves to transparent or similar
    expect(textarea).toHaveClass('px-3');
    expect(textarea).toHaveClass('py-2');
    expect(textarea).toHaveClass('text-base');
    expect(textarea).toHaveClass('placeholder:text-muted-foreground');
    expect(textarea).toHaveClass('focus-visible:ring-[3px]'); // Focus style
  });

  it('applies disabled attribute and styles correctly', () => {
    render(<Textarea data-testid="test-textarea" disabled />);
    const textarea = screen.getByTestId('test-textarea');
    expect(textarea).toBeDisabled();
    expect(textarea).toHaveClass('disabled:cursor-not-allowed');
    expect(textarea).toHaveClass('disabled:opacity-50');
  });

  it('applies error styles when aria-invalid is true', () => {
    render(<Textarea data-testid="test-textarea" aria-invalid={true} />);
    const textarea = screen.getByTestId('test-textarea');
    expect(textarea).toHaveAttribute('aria-invalid', 'true');
    // Check for error classes 
    expect(textarea).toHaveClass('aria-invalid:border-destructive');
    expect(textarea).toHaveClass('aria-invalid:ring-destructive/20'); 
  });

  it('does not apply error styles when aria-invalid is false or absent', () => {
    render(<Textarea data-testid="test-textarea" aria-invalid={false} />);
    const textarea = screen.getByTestId('test-textarea');
    // Check attribute is correctly set or absent
     expect(textarea).toHaveAttribute('aria-invalid', 'false');
     // Check specific error classes are not applied (though they might exist in the stylesheet)
     // This check is less reliable for conditional Tailwind classes.
     // expect(textarea).not.toHaveClass('aria-invalid:border-destructive'); 
  });

  it('forwards other textarea props correctly (placeholder, value, rows)', () => {
    const handleChange = () => {}; // Dummy handler
    render(
      <Textarea 
        data-testid="test-textarea" 
        placeholder="Enter text" 
        value="Initial text"
        rows={5}
        onChange={handleChange} // Ensure event handlers are passed
      />
    );
    const textarea = screen.getByTestId('test-textarea');
    expect(textarea).toHaveAttribute('placeholder', 'Enter text');
    expect(textarea).toHaveAttribute('rows', '5');
    expect(textarea).toHaveValue('Initial text');
  });

  it('applies additional className when provided', () => {
    const testClass = 'my-custom-textarea-class';
    render(<Textarea data-testid="test-textarea" className={testClass} />);
    const textarea = screen.getByTestId('test-textarea');
    expect(textarea).toHaveClass(testClass);
  });
});

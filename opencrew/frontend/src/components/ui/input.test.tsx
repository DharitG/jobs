import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Input } from './input'; // Adjust path as needed

describe('Input Component', () => {
  it('renders as an input element with default type text', () => {
    render(<Input data-testid="test-input" />);
    const input = screen.getByTestId('test-input');
    expect(input).toBeInTheDocument();
    expect(input.tagName.toLowerCase()).toBe('input');
    expect(input).toHaveAttribute('type', 'text');
  });

  it('applies base styling classes', () => {
    render(<Input data-testid="test-input" />);
    const input = screen.getByTestId('test-input');
    // Check for a selection of key base classes
    expect(input).toHaveClass('flex');
    expect(input).toHaveClass('h-9');
    expect(input).toHaveClass('w-full');
    expect(input).toHaveClass('rounded-design-md'); // Design system radius
    expect(input).toHaveClass('border');
    expect(input).toHaveClass('border-grey-20'); // Design system border color
    expect(input).toHaveClass('bg-background');
    expect(input).toHaveClass('px-3');
    expect(input).toHaveClass('py-1');
    expect(input).toHaveClass('text-base');
    expect(input).toHaveClass('text-grey-90'); // Design system text color
    expect(input).toHaveClass('placeholder:text-grey-40'); // Design system placeholder
    expect(input).toHaveClass('focus-visible:border-primary-500'); // Design system focus
    expect(input).toHaveClass('focus-visible:ring-primary-500/40'); // Design system focus ring
  });

  it('applies disabled attribute and styles correctly', () => {
    render(<Input data-testid="test-input" disabled />);
    const input = screen.getByTestId('test-input');
    expect(input).toBeDisabled();
    expect(input).toHaveClass('disabled:cursor-not-allowed');
    expect(input).toHaveClass('disabled:opacity-50');
  });

  it('applies error styles when aria-invalid is true', () => {
    render(<Input data-testid="test-input" aria-invalid={true} />);
    const input = screen.getByTestId('test-input');
    expect(input).toHaveAttribute('aria-invalid', 'true');
    // Check for error classes from design system
    expect(input).toHaveClass('aria-[invalid=true]:border-error');
    expect(input).toHaveClass('aria-[invalid=true]:ring-error/50');
  });

  it('sets aria-invalid attribute correctly when false or absent', () => {
    // Test when aria-invalid is explicitly false
    const { rerender } = render(<Input data-testid="test-input" aria-invalid={false} />);
    let input = screen.getByTestId('test-input');
    expect(input).toHaveAttribute('aria-invalid', 'false');

    // Test when aria-invalid is absent (should not have the attribute or be true)
    rerender(<Input data-testid="test-input" />);
    input = screen.getByTestId('test-input');
    expect(input).not.toHaveAttribute('aria-invalid', 'true'); 
    // Note: Depending on browser/jsdom, absent might mean no attribute or attribute="false"
    // We primarily care that it's not 'true'
  });

  it('forwards other input props correctly (type, placeholder, value)', () => {
    const handleChange = () => {}; // Dummy handler
    render(
      <Input 
        data-testid="test-input" 
        type="email" 
        placeholder="Enter email" 
        value="test@example.com"
        onChange={handleChange} // Ensure event handlers are passed
      />
    );
    const input = screen.getByTestId('test-input');
    expect(input).toHaveAttribute('type', 'email');
    expect(input).toHaveAttribute('placeholder', 'Enter email');
    expect(input).toHaveValue('test@example.com');
  });

  it('applies additional className when provided', () => {
    const testClass = 'my-custom-input-class';
    render(<Input data-testid="test-input" className={testClass} />);
    const input = screen.getByTestId('test-input');
    expect(input).toHaveClass(testClass);
  });
});

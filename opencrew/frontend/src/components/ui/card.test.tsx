import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardAction,
  CardDescription,
  CardContent,
} from './card'; // Adjust path as needed

describe('Card Components', () => {
  // Test Card component
  describe('Card', () => {
    it('renders children and applies base classes', () => {
      render(<Card data-testid="card-test">Card Content</Card>);
      const card = screen.getByTestId('card-test');
      expect(card).toBeInTheDocument();
      expect(screen.getByText('Card Content')).toBeInTheDocument();
      expect(card).toHaveClass('bg-card');
      expect(card).toHaveClass('text-card-foreground');
      expect(card).toHaveClass('rounded-xl');
      expect(card).toHaveClass('border');
      expect(card).toHaveClass('shadow-sm');
    });

    it('applies additional className', () => {
      render(<Card data-testid="card-test" className="my-custom-card">Content</Card>);
      expect(screen.getByTestId('card-test')).toHaveClass('my-custom-card');
    });
  });

  // Test CardHeader component
  describe('CardHeader', () => {
    it('renders children and applies base classes', () => {
      render(<CardHeader data-testid="header-test">Header Content</CardHeader>);
      const header = screen.getByTestId('header-test');
      expect(header).toBeInTheDocument();
      expect(screen.getByText('Header Content')).toBeInTheDocument();
      expect(header).toHaveClass('grid');
      expect(header).toHaveClass('px-6');
    });

    it('applies additional className', () => {
      render(<CardHeader data-testid="header-test" className="my-custom-header">Content</CardHeader>);
      expect(screen.getByTestId('header-test')).toHaveClass('my-custom-header');
    });
  });

  // Test CardTitle component
  describe('CardTitle', () => {
    it('renders children and applies base classes', () => {
      render(<CardTitle data-testid="title-test">Card Title</CardTitle>);
      const title = screen.getByTestId('title-test');
      expect(title).toBeInTheDocument();
      expect(screen.getByText('Card Title')).toBeInTheDocument();
      expect(title).toHaveClass('leading-none');
      expect(title).toHaveClass('font-semibold');
    });

    it('applies additional className', () => {
      render(<CardTitle data-testid="title-test" className="my-custom-title">Title</CardTitle>);
      expect(screen.getByTestId('title-test')).toHaveClass('my-custom-title');
    });
  });

  // Test CardDescription component
  describe('CardDescription', () => {
    it('renders children and applies base classes', () => {
      render(<CardDescription data-testid="desc-test">Card Description</CardDescription>);
      const desc = screen.getByTestId('desc-test');
      expect(desc).toBeInTheDocument();
      expect(screen.getByText('Card Description')).toBeInTheDocument();
      expect(desc).toHaveClass('text-muted-foreground');
      expect(desc).toHaveClass('text-sm');
    });

    it('applies additional className', () => {
      render(<CardDescription data-testid="desc-test" className="my-custom-desc">Desc</CardDescription>);
      expect(screen.getByTestId('desc-test')).toHaveClass('my-custom-desc');
    });
  });
  
  // Test CardAction component
  describe('CardAction', () => {
    it('renders children and applies base classes', () => {
      render(<CardAction data-testid="action-test">Action Item</CardAction>);
      const action = screen.getByTestId('action-test');
      expect(action).toBeInTheDocument();
      expect(screen.getByText('Action Item')).toBeInTheDocument();
      expect(action).toHaveClass('col-start-2'); // Example base class check
    });

    it('applies additional className', () => {
      render(<CardAction data-testid="action-test" className="my-custom-action">Action</CardAction>);
      expect(screen.getByTestId('action-test')).toHaveClass('my-custom-action');
    });
  });

  // Test CardContent component
  describe('CardContent', () => {
    it('renders children and applies base classes', () => {
      render(<CardContent data-testid="content-test">Card Content Area</CardContent>);
      const content = screen.getByTestId('content-test');
      expect(content).toBeInTheDocument();
      expect(screen.getByText('Card Content Area')).toBeInTheDocument();
      expect(content).toHaveClass('px-6');
    });

    it('applies additional className', () => {
      render(<CardContent data-testid="content-test" className="my-custom-content">Content</CardContent>);
      expect(screen.getByTestId('content-test')).toHaveClass('my-custom-content');
    });
  });

  // Test CardFooter component
  describe('CardFooter', () => {
    it('renders children and applies base classes', () => {
      render(<CardFooter data-testid="footer-test">Card Footer Info</CardFooter>);
      const footer = screen.getByTestId('footer-test');
      expect(footer).toBeInTheDocument();
      expect(screen.getByText('Card Footer Info')).toBeInTheDocument();
      expect(footer).toHaveClass('flex');
      expect(footer).toHaveClass('items-center');
      expect(footer).toHaveClass('px-6');
    });

    it('applies additional className', () => {
      render(<CardFooter data-testid="footer-test" className="my-custom-footer">Footer</CardFooter>);
      expect(screen.getByTestId('footer-test')).toHaveClass('my-custom-footer');
    });
  });

  // Test composition
  it('renders a complete card structure correctly', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Complete Card</CardTitle>
          <CardDescription>Description here</CardDescription>
        </CardHeader>
        <CardContent>
          <p>Main content goes here.</p>
        </CardContent>
        <CardFooter>
          Footer actions
        </CardFooter>
      </Card>
    );

    expect(screen.getByText('Complete Card')).toBeInTheDocument();
    expect(screen.getByText('Description here')).toBeInTheDocument();
    expect(screen.getByText('Main content goes here.')).toBeInTheDocument();
    expect(screen.getByText('Footer actions')).toBeInTheDocument();
  });
});

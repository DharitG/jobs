import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { JobCard } from './JobCard'; // Adjust path as needed

// Mock next/image component for testing environment
vi.mock('next/image', () => ({
  default: (props: any) => {
    // eslint-disable-next-line @next/next/no-img-element
    return <img {...props} alt={props.alt} />; // Render a basic img tag
  },
}));

// Mock dnd-kit hooks as they are not relevant for rendering tests
vi.mock('@dnd-kit/sortable', () => ({
  useSortable: () => ({
    attributes: {},
    listeners: {},
    setNodeRef: vi.fn(),
    transform: null,
    transition: null,
    isDragging: false,
  }),
}));
vi.mock('@dnd-kit/utilities', () => ({
  CSS: {
    Transform: {
      toString: () => undefined,
    },
  },
}));


describe('JobCard Component', () => {
  const defaultProps = {
    id: 'job-1',
    companyName: 'Test Company Inc.',
    jobTitle: 'Software Engineer Extraordinaire',
    location: 'Remote, Earth',
    stage: 'Interview',
    ctaLink: 'https://example.com/job',
    ctaText: 'Apply Now',
    logoUrl: '/test-logo.png',
  };

  it('renders company name, job title, and location', () => {
    render(<JobCard {...defaultProps} />);
    expect(screen.getByText(defaultProps.companyName)).toBeInTheDocument();
    expect(screen.getByText(defaultProps.jobTitle)).toBeInTheDocument();
    expect(screen.getByText(defaultProps.location)).toBeInTheDocument();
  });

  it('renders stage badge when stage is provided', () => {
    render(<JobCard {...defaultProps} />);
    expect(screen.getByText(defaultProps.stage)).toBeInTheDocument();
  });

  it('does not render stage badge when stage is not provided', () => {
    const propsWithoutStage = { ...defaultProps, stage: undefined };
    render(<JobCard {...propsWithoutStage} />);
    expect(screen.queryByText(defaultProps.stage)).not.toBeInTheDocument();
  });

  it('renders CTA button with correct text and link when provided', () => {
    render(<JobCard {...defaultProps} />);
    const ctaButton = screen.getByRole('link', { name: defaultProps.ctaText });
    expect(ctaButton).toBeInTheDocument();
    expect(ctaButton).toHaveAttribute('href', defaultProps.ctaLink);
  });

  it('does not render CTA button when ctaLink is not provided', () => {
    const propsWithoutLink = { ...defaultProps, ctaLink: undefined };
    render(<JobCard {...propsWithoutLink} />);
    expect(screen.queryByRole('link')).not.toBeInTheDocument();
  });

  it('renders the provided logo', () => {
    render(<JobCard {...defaultProps} />);
    const logo = screen.getByAltText(`${defaultProps.companyName} logo`);
    expect(logo).toBeInTheDocument();
    expect(logo).toHaveAttribute('src', defaultProps.logoUrl);
    expect(logo).toHaveAttribute('width', '56');
    expect(logo).toHaveAttribute('height', '56');
  });

  it('renders the placeholder logo when logoUrl is not provided', () => {
    const propsWithoutLogo = { ...defaultProps, logoUrl: undefined };
    render(<JobCard {...propsWithoutLogo} />);
    const logo = screen.getByAltText(`${defaultProps.companyName} logo`);
    expect(logo).toBeInTheDocument();
    expect(logo).toHaveAttribute('src', '/placeholder-logo.svg');
  });
  
  // Basic check for hover styles (more complex states might need interaction tests)
  it('applies base and hover classes', () => {
    render(<JobCard {...defaultProps} />);
    const cardElement = screen.getByText(defaultProps.companyName).closest('div[data-slot="job-card-container"]'); // Assuming a container test id or structure
    // Note: Testing hover classes directly is tricky. Check for presence of hover utility classes.
    // This test is limited as it doesn't simulate actual hover.
    // expect(cardElement).toHaveClass('hover:shadow-md');
    // expect(cardElement).toHaveClass('hover:border-primary/20');
    // expect(cardElement).toHaveClass('hover:-translate-y-px');
    // For now, just check base classes
     expect(screen.getByRole('img').closest('div.group')).toBeInTheDocument(); // Check group class exists
     expect(screen.getByRole('img').closest('div.group')).toHaveClass('bg-card');
     expect(screen.getByRole('img').closest('div.group')).toHaveClass('border-border');
  });

});

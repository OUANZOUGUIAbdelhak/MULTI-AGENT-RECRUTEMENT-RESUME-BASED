import { JobOffer } from '../types';

/**
 * Parse a job offer text file and extract structured information
 */
export function parseJobOfferFile(content: string, filename: string): JobOffer {
  const lines = content.split('\n').map((line) => line.trim()).filter((line) => line.length > 0);
  
  let title = '';
  let description = '';
  let requirements = '';
  let location = '';
  let salary = '';

  // Extract title (usually first or second line after "OFFRE D'EMPLOI")
  const offreIndex = lines.findIndex((line) => 
    line.toUpperCase().includes('OFFRE') || line.toUpperCase().includes('EMPLOI')
  );
  if (offreIndex >= 0 && offreIndex + 1 < lines.length) {
    title = lines[offreIndex + 1];
  } else if (lines.length > 0) {
    // Fallback: use first non-empty line
    title = lines[0];
  }

  // Extract location (look for "Localisation:" or "Location:")
  const locationLine = lines.find((line) => 
    line.toLowerCase().includes('localisation:') || 
    line.toLowerCase().includes('location:')
  );
  if (locationLine) {
    location = locationLine.split(':').slice(1).join(':').trim();
  }

  // Extract salary (look for "Salaire:" or "Salary:")
  const salaryLine = lines.find((line) => 
    line.toLowerCase().includes('salaire:') || 
    line.toLowerCase().includes('salary:')
  );
  if (salaryLine) {
    salary = salaryLine.split(':').slice(1).join(':').trim();
  }

  // Extract description sections
  const descriptionSections: string[] = [];
  let inDescriptionSection = false;
  let descriptionStartIndex = -1;

  // Look for common description section headers
  const descriptionHeaders = [
    'À PROPOS',
    'ABOUT',
    'VOTRE MISSION',
    'MISSION',
    'RESPONSABILITÉS',
    'RESPONSABILITIES',
    'DESCRIPTION',
  ];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].toUpperCase();
    
    // Check if we hit a description section
    if (descriptionHeaders.some((header) => line.includes(header))) {
      if (descriptionStartIndex === -1) {
        descriptionStartIndex = i;
      }
      inDescriptionSection = true;
      continue;
    }

    // Check if we hit requirements section (stop collecting description)
    if (
      line.includes('PROFIL') ||
      line.includes('PROFILE') ||
      line.includes('REQUIREMENTS') ||
      line.includes('COMPÉTENCES REQUISES') ||
      line.includes('QUALIFICATIONS')
    ) {
      if (inDescriptionSection && descriptionStartIndex >= 0) {
        descriptionSections.push(
          lines.slice(descriptionStartIndex, i).join('\n')
        );
      }
      inDescriptionSection = false;
      descriptionStartIndex = -1;
      break;
    }

    // Collect description content
    if (inDescriptionSection && descriptionStartIndex >= 0 && i > descriptionStartIndex) {
      // Continue collecting
    }
  }

  // If we're still in a description section, collect until end or requirements
  if (inDescriptionSection && descriptionStartIndex >= 0) {
    const requirementsStart = lines.findIndex((line, idx) => 
      idx > descriptionStartIndex && (
        line.toUpperCase().includes('PROFIL') ||
        line.toUpperCase().includes('REQUIREMENTS') ||
        line.toUpperCase().includes('COMPÉTENCES')
      )
    );
    
    const endIndex = requirementsStart >= 0 ? requirementsStart : lines.length;
    descriptionSections.push(
      lines.slice(descriptionStartIndex, endIndex).join('\n')
    );
  }

  description = descriptionSections.join('\n\n').trim();

  // Extract requirements section
  const requirementsHeaders = [
    'PROFIL RECHERCHÉ',
    'PROFILE REQUIRED',
    'REQUIREMENTS',
    'COMPÉTENCES REQUISES',
    'QUALIFICATIONS',
  ];

  let requirementsStartIndex = -1;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].toUpperCase();
    if (requirementsHeaders.some((header) => line.includes(header))) {
      requirementsStartIndex = i;
      break;
    }
  }

  if (requirementsStartIndex >= 0) {
    // Collect until we hit certain sections that indicate end of requirements
    const endSections = ['LANGUES', 'LANGUAGES', 'AVANTAGES', 'BENEFITS', 'PROCESSUS', 'PROCESS'];
    let requirementsEndIndex = lines.length;
    
    for (let i = requirementsStartIndex + 1; i < lines.length; i++) {
      const line = lines[i].toUpperCase();
      if (endSections.some((section) => line.includes(section))) {
        requirementsEndIndex = i;
        break;
      }
    }
    
    requirements = lines.slice(requirementsStartIndex, requirementsEndIndex).join('\n').trim();
  }

  // Fallback: if we couldn't parse well, use the whole content intelligently
  if (!title || !description || !requirements) {
    // Try to extract title from filename
    if (!title && filename) {
      title = filename
        .replace(/\.(txt|pdf)$/i, '')
        .replace(/[_-]/g, ' ')
        .split(' ')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    }

    // Use first part as description, second part as requirements
    const midPoint = Math.floor(lines.length / 2);
    if (!description) {
      description = lines.slice(0, midPoint).join('\n');
    }
    if (!requirements) {
      requirements = lines.slice(midPoint).join('\n');
    }
  }

  return {
    title: title || 'Job Offer',
    description: description || content,
    requirements: requirements || 'See job description',
    location: location || '',
    salary: salary || '',
  };
}


import React from 'react';

const PrivacyPolicyPage = () => {
  return (
    // Removed Layout wrapper as it's handled by root layout
    <div className="container mx-auto px-4 py-8 pt-24"> {/* Added pt-24 for spacing below navbar */}
      <h1 className="text-3xl font-bold mb-6">Privacy Policy</h1>
      <p className="mb-4">Last Updated: April 19, 2025</p>

      <h2 className="text-2xl font-semibold mt-6 mb-3">1. Introduction</h2>
      <p className="mb-4">
        Welcome to OpenCrew ("we," "us," or "our"). We are committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our website and services (collectively, the "Service"). Please read this privacy policy carefully. If you do not agree with the terms of this privacy policy, please do not access the Service.
      </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">2. Information We Collect</h2>
        <p className="mb-4">We may collect information about you in a variety of ways. The information we may collect via the Service includes:</p>
        <ul className="list-disc list-inside mb-4 space-y-2">
          <li>
            <strong>Personal Data:</strong> Personally identifiable information, such as your name and email address, that you voluntarily give to us when you register with the Service (e.g., via our authentication provider) or when you choose to participate in various activities related to the Service.
          </li>
          <li>
            <strong>Resume and Application Data:</strong> Information you provide related to your job search, including resume content (text and potentially temporary file formats during processing), links to external profiles or portfolios, job application history, status updates, and notes you add regarding applications.
          </li>
          <li>
            <strong>Subscription and Payment Data:</strong> Information related to your subscription tier and payment details necessary to process payments through our third-party payment processor (e.g., payment processor identifiers). We do not directly store your full credit card information.
          </li>
          <li>
            <strong>Job Data:</strong> Information about job postings that we collect through automated means from publicly available sources or third-party job boards. This may include job titles, company names, locations, descriptions, and URLs.
          </li>
          <li>
            <strong>Derivative Data:</strong> Information our servers automatically collect when you access the Service, such as your IP address, browser type, operating system, access times, and the pages you have viewed directly before and after accessing the Service. We may also collect information about your interactions with the Service features.
          </li>
          <li>
            <strong>Data From Third Parties:</strong> We may receive information about you from third parties, such as our authentication provider when you register or log in.
          </li>
        </ul>

        <h2 className="text-2xl font-semibold mt-6 mb-3">3. How We Use Your Information</h2>
        <p className="mb-4">Having accurate information about you permits us to provide you with a smooth, efficient, and customized experience. Specifically, we may use information collected about you via the Service to:</p>
        <ul className="list-disc list-inside mb-4 space-y-2">
          <li>Create and manage your account.</li>
          <li>Process your payments and subscriptions.</li>
          <li>Provide the core functionalities of the Service, including job tracking, resume storage, and application management.</li>
          <li>Utilize automated systems and semantic analysis technology to match your profile and resume data with job descriptions.</li>
          <li>Offer features that assist in optimizing your resume content, potentially utilizing third-party AI services for suggestions (see Section 4).</li>
          <li>Facilitate the automated submission of job applications on your behalf and at your explicit direction to external Applicant Tracking Systems (ATS) or career sites (see Section 4 and our Terms of Service).</li>
          <li>Communicate with you regarding your account or requested services.</li>
          <li>Monitor and analyze usage and trends to improve your experience with the Service.</li>
          <li>Compile anonymous statistical data and analysis for use internally or with third parties.</li>
          <li>Prevent fraudulent transactions, monitor against theft, and protect against criminal activity.</li>
          <li>Comply with legal and regulatory requirements.</li>
        </ul>

        <h2 className="text-2xl font-semibold mt-6 mb-3">4. AI Data Processing and Automated Features</h2>
        <p className="mb-4">
          Our Service utilizes automated systems, including artificial intelligence (AI) and semantic analysis technologies, to provide certain features. This involves processing your data in specific ways:
        </p>
        <ul className="list-disc list-inside mb-4 space-y-2">
          <li>
            <strong>Semantic Matching:</strong> We use internal semantic analysis technology to process the text content of your resume(s) and job descriptions. This generates numerical representations (embeddings) which are stored in a specialized database to facilitate efficient matching between your profile and relevant job opportunities based on semantic similarity.
          </li>
          <li>
            <strong>Resume Optimization Assistance:</strong> To provide suggestions for improving your resume, we may send snippets of your resume text to a third-party AI service provider. This provider processes the text to generate alternative phrasing or content suggestions. We only send the necessary text portions for this feature.
          </li>
          <li>
            <strong>Automated Application Assistance:</strong> When you utilize our automated application submission feature, our systems, potentially including semantic analysis technology, assist in identifying and filling form fields on external websites using the information you have provided (e.g., resume data, personal details). Your data is transmitted to these external sites as part of the application process initiated by you.
          </li>
        </ul>
        <p className="mb-4">
          By using these features, you acknowledge and consent to the processing described above.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">5. Data Sharing and Disclosure</h2>
        <p className="mb-4">We may share information we have collected about you in certain situations. Your information may be disclosed as follows:</p>
        <ul className="list-disc list-inside mb-4 space-y-2">
          <li>
            <strong>By Law or to Protect Rights:</strong> If we believe the release of information about you is necessary to respond to legal process, to investigate or remedy potential violations of our policies, or to protect the rights, property, and safety of others, we may share your information as permitted or required by any applicable law, rule, or regulation.
          </li>
          <li>
            <strong>Third-Party Service Providers:</strong> We may share your information with third parties that perform services for us or on our behalf, including payment processing (e.g., Stripe), data analysis, email delivery, hosting services, customer service, authentication services (e.g., Auth0), vector database hosting (if applicable), and AI service providers (for specific features like resume optimization). We require our third-party service providers to use your personal information only as necessary to provide the services we have requested.
          </li>
          <li>
            <strong>External Websites/ATS (Auto-Application):</strong> When you explicitly authorize and initiate the use of our automated application submission feature for a specific job, we will transmit your relevant personal information and resume data to the corresponding external company website or Applicant Tracking System (ATS) as required to complete the application form. We do not control the privacy practices of these external sites.
          </li>
          <li>
            <strong>Business Transfers:</strong> We may share or transfer your information in connection with, or during negotiations of, any merger, sale of company assets, financing, or acquisition of all or a portion of our business to another company.
          </li>
          <li>
            <strong>Affiliates:</strong> We may share your information with our affiliates, in which case we will require those affiliates to honor this Privacy Policy. Affiliates include our parent company and any subsidiaries, joint venture partners or other companies that we control or that are under common control with us.
          </li>
          <li>
            <strong>With Your Consent:</strong> We may disclose your personal information for any other purpose with your consent.
          </li>
        </ul>
        <p className="mb-4">We do not sell your personal information.</p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">6. Data Storage and Security</h2>
        <p className="mb-4">
          We use administrative, technical, and physical security measures to help protect your personal information. We store your data in secure databases and potentially specialized vector databases. Temporary files created during processing (e.g., resume uploads) are handled securely and deleted promptly after use. While we have taken reasonable steps to secure the personal information you provide to us, please be aware that despite our efforts, no security measures are perfect or impenetrable, and no method of data transmission can be guaranteed against any interception or other type of misuse. Any information disclosed online is vulnerable to interception and misuse by unauthorized parties. Therefore, we cannot guarantee complete security if you provide personal information.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">7. User Rights</h2>
        <p className="mb-4">
          Depending on your location, you may have certain rights regarding your personal information. These may include the right to:
        </p>
        <ul className="list-disc list-inside mb-4 space-y-2">
          <li>Request access to the personal information we hold about you.</li>
          <li>Request correction of inaccurate or incomplete information.</li>
          <li>Request deletion of your personal information, subject to certain exceptions.</li>
          <li>Object to or restrict certain processing activities.</li>
          <li>Request the transfer of your personal information to another party (data portability).</li>
        </ul>
        <p className="mb-4">
          To exercise these rights, please contact us using the contact information provided below. We may need to verify your identity before processing your request. We will respond to your request within the timeframe required by applicable law.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">8. Cookies and Tracking Technologies</h2>
        <p className="mb-4">
          We may use cookies, web beacons, tracking pixels, and other tracking technologies on the Service to help customize the Service and improve your experience. When you access the Service, your personal information is not collected through the use of tracking technology. Most browsers are set to accept cookies by default. You can usually choose to set your browser to remove or reject browser cookies. Please note that if you choose to remove or reject cookies, this could affect the availability and functionality of the Service.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">9. Children's Privacy</h2>
        <p className="mb-4">
          Our Service is not intended for use by children under the age of 13 (or 16 in certain jurisdictions). We do not knowingly collect personal information from children under these ages. If we become aware that we have collected personal information from a child under the relevant age without verification of parental consent, we will take steps to remove that information from our servers.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">10. Changes to This Policy</h2>
        <p className="mb-4">
          We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last Updated" date. You are advised to review this Privacy Policy periodically for any changes. Changes to this Privacy Policy are effective when they are posted on this page.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">11. Contact Information</h2>
        <p className="mb-4">
          If you have questions or comments about this Privacy Policy, please contact us at: support@opencrew.io
        </p>
      </div>
    // Removed Layout wrapper
  );
};

export default PrivacyPolicyPage;

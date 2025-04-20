import React from 'react';

const TermsOfServicePage = () => {
  return (
    // Removed Layout wrapper as it's handled by root layout
    <div className="container mx-auto px-4 py-8 pt-24"> {/* Added pt-24 for spacing below navbar */}
      <h1 className="text-3xl font-bold mb-6">Terms of Service</h1>
      <p className="mb-4">Last Updated: April 19, 2025</p>

      <h2 className="text-2xl font-semibold mt-6 mb-3">1. Acceptance of Terms</h2>
      <p className="mb-4">
        By accessing or using the OpenCrew website and services (collectively, the "Service"), you agree to be bound by these Terms of Service ("Terms") and our Privacy Policy. If you do not agree to these Terms, do not use the Service. These Terms constitute a legally binding agreement between you and OpenCrew Inc. ("we," "us," or "our").
      </p>

      <h2 className="text-2xl font-semibold mt-6 mb-3">2. Description of Service</h2>
      <p className="mb-4">
        The Service provides users with tools to manage their job search process, including but not limited to: tracking job applications, storing and managing resume information, utilizing semantic analysis technology for job matching suggestions, accessing features for resume content optimization assistance, utilizing automated job data collection from public sources, and optionally enabling automated assistance for submitting job applications to third-party websites ("Auto-Application Feature"). Features and subscription tiers may vary.
      </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">3. User Accounts</h2>
        <p className="mb-4">
          To access certain features of the Service, you may need to register for an account, potentially through a third-party authentication provider. You agree to provide accurate, current, and complete information during the registration process and to update such information to keep it accurate, current, and complete. You are responsible for safeguarding your account password and for any activities or actions under your account. You agree to notify us immediately of any unauthorized use of your account.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">4. User Responsibilities</h2>
        <ul className="list-disc list-inside mb-4 space-y-2">
          <li>You are solely responsible for the accuracy, content, and legality of all information you provide, including your resume data and personal details.</li>
          <li>You agree to use the Service only for lawful purposes and in accordance with these Terms and any applicable laws.</li>
          <li>You represent and warrant that you have the necessary rights and permissions to upload and use any content you provide, including resume information.</li>
          <li>You are responsible for reviewing and verifying the accuracy of any suggestions provided by our resume optimization features before using them.</li>
          <li>If you choose to use the Auto-Application Feature, you are solely responsible for ensuring you have the right to apply for the selected positions and that the information submitted is accurate and complete.</li>
        </ul>

        <h2 className="text-2xl font-semibold mt-6 mb-3">5. Auto-Application Feature</h2>
        <p className="mb-4">
          The Service may offer an optional Auto-Application Feature that uses automated systems (e.g., browser automation tools) to assist in filling out and submitting job applications on external, third-party Applicant Tracking Systems (ATS) or company career websites using the information you have provided and stored within the Service.
        </p>
        <ul className="list-disc list-inside mb-4 space-y-2">
          <li><strong>Explicit Authorization Required:</strong> You must explicitly authorize the use of the Auto-Application Feature for each application you wish to submit using this method. By authorizing, you instruct us to act as your agent to submit the application on your behalf using your provided data.</li>
          <li><strong>Acknowledgement of Risks:</strong> You acknowledge and agree that the use of automated tools to interact with third-party websites carries inherent risks. These include, but are not limited to:
            <ul className="list-disc list-inside ml-6 space-y-1">
              <li>Potential errors in data entry or submission.</li>
              <li>Possible violation of the terms of service of the target ATS or website, which could lead to application rejection or account suspension on those platforms.</li>
              <li>Technical failures or interruptions preventing successful submission.</li>
              <li>Changes in the layout or functionality of external websites rendering the automation ineffective or inaccurate.</li>
            </ul>
          </li>
          <li><strong>User Responsibility for Verification:</strong> You are strongly encouraged to verify the successful submission and accuracy of any application submitted using the Auto-Application Feature directly with the target company or on the relevant platform.</li>
          <li><strong>Disclaimer:</strong> We provide the Auto-Application Feature as a convenience tool. We do not guarantee successful submission, accuracy, or acceptance of any application submitted using this feature. We are not responsible for the terms, policies, or practices of any third-party websites or ATS. Your use of the Auto-Application Feature is entirely at your own risk. See also Sections 10 and 11 regarding Disclaimers and Limitation of Liability.</li>
        </ul>

        <h2 className="text-2xl font-semibold mt-6 mb-3">6. Job Scraping and Third-Party Data</h2>
        <p className="mb-4">
          The Service may automatically collect job posting information from publicly available sources or third-party job boards. While we strive for accuracy, we do not guarantee the timeliness, completeness, or accuracy of this scraped data. Job availability and details are subject to change without notice by the posting entity. We are not responsible for the content or practices of third-party job sites.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">7. Subscription Tiers & Payment</h2>
        <p className="mb-4">
          Access to certain features or usage levels (e.g., quotas for resume optimizations or auto-applications) may require a paid subscription. Subscription details, including fees, billing cycles, and included features/quotas, will be presented at the time of purchase. Payments are processed through a third-party payment processor (e.g., Stripe). By providing payment information, you authorize us (or our processor) to charge the applicable fees. Subscriptions may automatically renew unless cancelled prior to the renewal date according to the terms presented. You are responsible for all applicable taxes. We reserve the right to change subscription fees upon reasonable notice.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">8. Intellectual Property</h2>
        <p className="mb-4">
          The Service and its original content (excluding User Content), features, and functionality are and will remain the exclusive property of OpenCrew Inc. and its licensors. The Service is protected by copyright, trademark, and other laws of both the United States and foreign countries. Our trademarks and trade dress may not be used in connection with any product or service without our prior written consent. You retain ownership of the content you submit to the Service ("User Content"), but you grant us a worldwide, non-exclusive, royalty-free license to use, copy, reproduce, process, adapt, modify, publish, transmit, display, and distribute your User Content solely for the purpose of providing and improving the Service.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">9. Prohibited Conduct</h2>
        <p className="mb-4">You agree not to engage in any of the following prohibited activities:</p>
        <ul className="list-disc list-inside mb-4 space-y-2">
          <li>Using the Service for any illegal purpose or in violation of any local, state, national, or international law.</li>
          <li>Violating or encouraging others to violate the rights of third parties, including intellectual property rights.</li>
          <li>Posting, uploading, or distributing any content that is unlawful, defamatory, libelous, inaccurate, or that a reasonable person could deem to be objectionable, profane, indecent, pornographic, harassing, threatening, hateful, or otherwise inappropriate.</li>
          <li>Interfering with security-related features of the Service.</li>
          <li>Interfering with the operation of the Service or any user's enjoyment of it, including by uploading or otherwise disseminating viruses, adware, spyware, worms, or other malicious code, making unsolicited offers or advertisements, or attempting to collect personal information about users or third parties without their consent.</li>
          <li>Accessing, monitoring, or copying any content or information of the Service using any robot, spider, scraper, or other automated means or any manual process for any purpose without our express written permission.</li>
          <li>Performing any fraudulent activity, including impersonating any person or entity, claiming false affiliations, or accessing the accounts of others without permission.</li>
          <li>Attempting to decipher, decompile, disassemble, or reverse engineer any of the software used to provide the Service.</li>
        </ul>

        <h2 className="text-2xl font-semibold mt-6 mb-3">10. Disclaimers of Warranty</h2>
        <p className="mb-4">
          THE SERVICE IS PROVIDED ON AN "AS IS" AND "AS AVAILABLE" BASIS. YOUR USE OF THE SERVICE IS AT YOUR SOLE RISK. TO THE FULLEST EXTENT PERMITTED BY APPLICABLE LAW, WE EXPRESSLY DISCLAIM ALL WARRANTIES OF ANY KIND, WHETHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE, AND NON-INFRINGEMENT.
        </p>
        <p className="mb-4">
          WE DO NOT WARRANT THAT: (A) THE SERVICE WILL MEET YOUR REQUIREMENTS; (B) THE SERVICE WILL BE UNINTERRUPTED, TIMELY, SECURE, OR ERROR-FREE; (C) THE RESULTS THAT MAY BE OBTAINED FROM THE USE OF THE SERVICE (INCLUDING JOB MATCHES, RESUME SUGGESTIONS, OR AUTO-APPLICATION SUCCESS) WILL BE ACCURATE, RELIABLE, OR GUARANTEE ANY PARTICULAR OUTCOME (SUCH AS JOB OFFERS); OR (D) THE QUALITY OF ANY PRODUCTS, SERVICES, INFORMATION, OR OTHER MATERIAL PURCHASED OR OBTAINED BY YOU THROUGH THE SERVICE WILL MEET YOUR EXPECTATIONS.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">11. Limitation of Liability</h2>
        <p className="mb-4">
          TO THE FULLEST EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL OpenCrew Inc., ITS AFFILIATES, DIRECTORS, EMPLOYEES, AGENTS, OR LICENSORS BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR EXEMPLARY DAMAGES, INCLUDING BUT NOT LIMITED TO, DAMAGES FOR LOSS OF PROFITS, GOODWILL, USE, DATA, OR OTHER INTANGIBLE LOSSES (EVEN IF WE HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES), RESULTING FROM: (A) THE USE OR THE INABILITY TO USE THE SERVICE; (B) THE COST OF PROCUREMENT OF SUBSTITUTE GOODS AND SERVICES RESULTING FROM ANY GOODS, DATA, INFORMATION, OR SERVICES PURCHASED OR OBTAINED OR MESSAGES RECEIVED OR TRANSACTIONS ENTERED INTO THROUGH OR FROM THE SERVICE; (C) UNAUTHORIZED ACCESS TO OR ALTERATION OF YOUR TRANSMISSIONS OR DATA; (D) STATEMENTS OR CONDUCT OF ANY THIRD PARTY ON THE SERVICE (INCLUDING EXTERNAL ATS OR JOB SITES); (E) THE USE OR OUTCOMES OF THE AUTO-APPLICATION FEATURE OR RELIANCE ON SCRAPED JOB DATA; OR (F) ANY OTHER MATTER RELATING TO THE SERVICE.
        </p>
        <p className="mb-4">
          IN NO EVENT SHALL OUR TOTAL LIABILITY TO YOU FOR ALL DAMAGES, LOSSES, AND CAUSES OF ACTION EXCEED THE AMOUNT YOU HAVE PAID US IN THE LAST SIX (6) MONTHS, OR, IF GREATER, ONE HUNDRED U.S. DOLLARS ($100).
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">12. Indemnification</h2>
        <p className="mb-4">
          You agree to defend, indemnify, and hold harmless OpenCrew Inc. and its affiliates, officers, directors, employees, and agents from and against any and all claims, damages, obligations, losses, liabilities, costs or debt, and expenses (including but not limited to attorney's fees) arising from: (a) your use of and access to the Service; (b) your violation of any term of these Terms; (c) your violation of any third-party right, including without limitation any copyright, property, or privacy right; or (d) any claim that your User Content caused damage to a third party. This defense and indemnification obligation will survive these Terms and your use of the Service.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">13. Termination</h2>
        <p className="mb-4">
          We may terminate or suspend your access to the Service immediately, without prior notice or liability, for any reason whatsoever, including without limitation if you breach the Terms. Upon termination, your right to use the Service will immediately cease. If you wish to terminate your account, you may simply discontinue using the Service or contact us. All provisions of the Terms which by their nature should survive termination shall survive termination, including, without limitation, ownership provisions, warranty disclaimers, indemnity, and limitations of liability.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">14. Governing Law & Dispute Resolution</h2>
        <p className="mb-4">
          These Terms shall be governed and construed in accordance with the laws of the State of Delaware, without regard to its conflict of law provisions. Any dispute arising from or relating to the subject matter of these Terms shall be finally settled by arbitration in San Francisco, California, using the English language in accordance with the JAMS Streamlined Arbitration Rules and Procedures then in effect.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">15. Changes to Terms</h2>
        <p className="mb-4">
          We reserve the right, at our sole discretion, to modify or replace these Terms at any time. If a revision is material, we will provide at least 30 days' notice prior to any new terms taking effect. What constitutes a material change will be determined at our sole discretion. By continuing to access or use our Service after any revisions become effective, you agree to be bound by the revised terms. If you do not agree to the new terms, you are no longer authorized to use the Service.
        </p>

        <h2 className="text-2xl font-semibold mt-6 mb-3">16. Contact Information</h2>
        <p className="mb-4">
          If you have any questions about these Terms, please contact us at: support@opencrew.io
        </p>
      </div>
    // Removed Layout wrapper
  );
};

export default TermsOfServicePage;

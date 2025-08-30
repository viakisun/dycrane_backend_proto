import React from 'react';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <div className="p-4 md:p-6 lg:p-8 max-w-4xl mx-auto">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-gray-800">DY Crane Safety Management</h1>
        <p className="text-lg text-gray-500 mt-2">
          Developer Portal & Project Dashboard
        </p>
      </header>

      <section className="mb-10">
        <p className="text-base text-gray-700 leading-relaxed">
          Welcome to the developer portal for the DY Crane Safety Management project. This application serves two primary purposes: it is the backend API for the safety management system, and it provides a suite of tools to help developers understand, test, and contribute to the project.
        </p>
      </section>

      <section>
        <h2 className="text-2xl font-bold text-gray-700 mb-4 border-b pb-2">Key Resources</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          <ResourceCard
            title="Interactive Test Client"
            description="The best way to understand the business logic. A step-by-step visual tool to run the entire E2E workflow."
            link="/test-client"
            linkLabel="Launch Test Client"
          />

          <ResourceCard
            title="API Specification (Swagger)"
            description="The complete OpenAPI (Swagger) specification for the backend API. Details all endpoints, request payloads, and response models."
            link="/openapi.yaml"
            linkLabel="View openapi.yaml"
            isExternal={true}
          />

          <ResourceCard
            title="Contribution Guide"
            description="The essential guide for new developers. Explains how to set up the environment, run tests, and submit changes."
            link="/CONTRIBUTING.md"
            linkLabel="Read CONTRIBUTING.md"
            isExternal={true}
          />

          <ResourceCard
            title="Test Client Guide"
            description="A detailed breakdown of the business logic behind each step (A1-F2) in the interactive test client."
            link="/TEST_CLIENT_GUIDE.md"
            linkLabel="Read the Guide"
            isExternal={true}
          />

        </div>
      </section>
    </div>
  );
};

interface ResourceCardProps {
    title: string;
    description: string;
    link: string;
    linkLabel: string;
    isExternal?: boolean;
}

const ResourceCard: React.FC<ResourceCardProps> = ({ title, description, link, linkLabel, isExternal }) => {
    const linkProps = isExternal ? { href: link, target: '_blank', rel: 'noopener noreferrer' } : {};

    const linkElement = isExternal ? (
        <a {...linkProps} className="font-medium text-blue-600 hover:underline">
            {linkLabel} &rarr;
        </a>
    ) : (
        <Link to={link} className="font-medium text-blue-600 hover:underline">
            {linkLabel} &rarr;
        </Link>
    );

    return (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 flex flex-col">
            <h3 className="text-lg font-bold text-gray-800 mb-2">{title}</h3>
            <p className="text-sm text-gray-600 flex-grow mb-4">{description}</p>
            {linkElement}
        </div>
    );
}


export default HomePage;

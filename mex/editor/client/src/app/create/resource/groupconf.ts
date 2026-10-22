/**
 * groupConf API documentation.
 */
export const groupConf = {
  activity: {
    categories: [
      {
        id: "general",
        properties: ["alternativeTitle", "activityType", "abstract", "title"],
        title: "General",
      },
      {
        id: "creators",
        properties: ["involvedPerson", "responsibleUnit", "involvedUnit"],
        title: "Creators & Contributors",
      },
      {
        id: "description",
        properties: ["start", "end", "theme"],
        title: "Description",
      },
      {
        id: "partners",
        properties: ["externalAssociate", "funderOrCommissioner", "fundingProgram"],
        title: "Partners & Funding",
      },
      {
        id: "publication",
        properties: ["publication", "documentation", "website"],
        title: "Related Publications & Further Documentation",
      },
      {
        id: "relatedResources",
        properties: ["isPartOfActivity", "succeeds", "relatedActivity", "wasGeneratedBy"],
        title: "Related Resources",
      },
      {
        id: "contact",
        properties: ["contact"],
        title: "Contact",
      },
    ],
  },
  bibliographicResource: {
    categories: [
      {
        id: "general",
        properties: [
          "alternativeTitle",
          "language",
          "abstract",
          "bibliographicResourceType",
          "issued",
          "title",
        ],
        title: "General",
      },
      {
        id: "creators",
        properties: ["creator", "contributingUnit"],
        title: "Creators",
      },
      {
        id: "keywords",
        properties: ["keyword"],
        title: "Keywords",
      },
      {
        id: "titleProper",
        properties: [
          "journal",
          "issue",
          "volume",
          "titleOfBook",
          "subtitle",
          "titleOfSeries",
          "volumeOfSeries",
          "section",
        ],
        title: "Title Proper",
      },
      {
        id: "imprint",
        properties: [
          "publisher",
          "publicationPlace",
          "publicationYear",
          "edition",
          "pages",
          "isbnIssn",
        ],
        title: "Imprint",
      },
      {
        id: "editor",
        properties: ["editor", "editorOfSeries"],
        title: "Editor",
      },
      {
        id: "relatedResources",
        properties: ["publication"],
        title: "Related Resources",
      },
      {
        id: "access",
        properties: ["accessRestriction", "doi", "alternateIdentifier", "repositoryURL", "license"],
        title: "Access & Usage Rights",
      },
      {
        id: "files",
        properties: ["distribution"],
        title: "Files",
      },
    ],
  },
  resource: {
    categories: [
      {
        id: "general",
        properties: [
          "resourceTypeSpecific",
          "resourceTypeGeneral",
          "created",
          "alternativeTitle",
          "description",
          "language",
          "modified",
          "meshId",
          "loincId",
          "icd10code",
          "title",
        ],
        title: "General",
      },
      {
        id: "creators",
        properties: [
          "creator",
          "unitInCharge",
          "contributor",
          "contributingUnit",
          "externalPartner",
        ],
        title: "Creators & Contributors",
      },
      {
        id: "keywords",
        properties: ["theme", "healthCategory", "keyword"],
        title: "Theme & Keywords",
      },
      {
        id: "coverage",
        properties: [
          "temporal",
          "start",
          "end",
          "spatial",
          "minTypicalAge",
          "maxTypicalAge",
          "populationCoverage",
          "sizeOfDataBasis",
          "numberOfRecords",
          "numberOfUniqueIndividuals",
        ],
        title: "Data Representation & Coverage",
      },
      {
        id: "legal",
        properties: ["hasLegalBasis", "hasPurpose", "provenance", "hasPersonalData", "source"],
        title: "Legal Basis & Data Provenance",
      },
      {
        id: "processing",
        properties: [
          "resourceCreationMethod",
          "accrualPeriodicity",
          "anonymizationPseudonymization",
          "instrumentToolOrApparatus",
        ],
        title: "Data Collection & Processing",
      },
      {
        id: "quality",
        properties: ["conformsTo", "qualityInformation", "hasCodeValues", "analytics", "sample"],
        title: "Standards & Quality",
      },
      {
        id: "methodology",
        properties: ["method", "methodDescription"],
        title: "Methodology",
      },
      {
        id: "publication",
        properties: ["publication", "documentation"],
        title: "Related Publications & Further Documentation",
      },
      {
        id: "generatedBy",
        properties: ["wasGeneratedBy"],
        title: "Related Projects",
      },
      {
        id: "relatedResources",
        properties: ["isPartOf", "relatedResource"],
        title: "Related Resources",
      },
      {
        id: "contact",
        properties: ["contact"],
        title: "Contact",
      },
      {
        id: "access",
        properties: ["accessRestriction", "doi", "license", "rights"],
        title: "Access & Usage Rights",
      },
      {
        id: "files",
        properties: ["distribution"],
        title: "Files",
      },
      {
        id: "variables",
        properties: ["usedIn"],
        title: "Variables",
      },
    ],
  },
};

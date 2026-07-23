/**
 * Model to store person create data.
 */
export interface CreatePerson {
  $createtype: "person";
  firstname: string;
  lastname: string;
}

/**
 * Model to store mail create data.
 */
export interface CreateMail {
  $createtype: "mail";
  email: string;
}

/**
 * Union type for all createable contacts.
 */
export type CreateContact = CreatePerson | CreateMail;

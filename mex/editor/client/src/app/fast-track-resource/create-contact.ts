export interface CreatePerson {
  $createtype: "person";
  firstname: string;
  lastname: string;
}

export interface CreateMail {
  $createtype: "mail";
  email: string;
}

export type CreateContact = CreatePerson | CreateMail;

export interface CreateContactPointModel {
  $type: "CreateContactPointModel";
  email: string;
}

export interface CreatePersonModel {
  $type: "CreatePersonModel";
  firstName: number;
  lastName: number;
}

export interface FastTrackActivityModel {
  title: string;
  contact: (string | CreateContactPointModel | CreatePersonModel)[];
}

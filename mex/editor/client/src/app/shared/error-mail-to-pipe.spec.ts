import { ErrorMailToPipe } from "./error-mail-to-pipe";

describe("MailToPipe", () => {
  it("create an instance", () => {
    const pipe = new ErrorMailToPipe();
    expect(pipe).toBeTruthy();
  });
});

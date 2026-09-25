import { JsonPipe } from "@angular/common";
import { httpResource } from "@angular/common/http";
import { Component, input } from "@angular/core";

@Component({
  selector: "mex-edit",
  imports: [JsonPipe],
  templateUrl: "./edit.html",
  styleUrl: "./edit.scss",
})
/**
 * Page to edit entities.
 */
export class Edit {
  // 3m51ZHwqj6PAiOBwATefM
  entityId = input.required<string>();
  entity = httpResource<{ stableTargetId: string }>(
    () => `api/v0/backend/rule-set/${this.entityId()}`,
    {
      defaultValue: { stableTargetId: "NONE" },
    },
  );
}

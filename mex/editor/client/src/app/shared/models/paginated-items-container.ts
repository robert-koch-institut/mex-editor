/**
 * Model to store paginated data containing total count.
 */
export interface PaginatedItemsContainer<T> {
  items: T[];
  total: number;
}

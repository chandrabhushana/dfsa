
With the addition of the new render helpers (modified from the core), view tests have been 
combined with controller tests to take advantage of the business logic already in place there.

However for a fully robust suite, view tests using a browser driver (selenium) should be 
created in the future (time permitting), that unobtrusively test the remote site when deployed to the GAE dev server, 
to be run before deploying to production GAE. 


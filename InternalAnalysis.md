The content in the {extracted_text} is called an SFS. It is a functional specfication used to create a product by engineers. It is also used to document user guides by writers. However, because of its mutliple users, a writer needs to be careful about what information is taken from it. Usually, a writer focuses on sectioins of the document called End User Interface/User Experience, Problem Statement, Functional Requirements Summary for the meat of the user guide.

The object of this exercise is to find out what information should not be exposed to the customer. Make a list of this and give it to the writer, explaining that these are the things you do not plan to use in the document. This could be any of the following.

- Implementation logic
- Internal architecture
- Debug hooks
- Private APIs
- Database schemas
- Internal error codes
- Engineering workarounds
- Code-level implementation details
- Backend processes
- Internal service dependencies
- Memory dumps or stack traces
- Kernel-level debugging information
- Internal testing procedures

There is no need to list the above list. 

Here is how your Ouput should look like:

- A list of information types that you are sure should not be used in the user guide
- List of information types you are unsure of, and do not know whether to use in a user guide. This is optional, and needed only if you are truly in doubt. 

Ask to proceed to the next step.

#Devpost API
###Endpoints
- /hackathons/ 
  - Return a list of hackathons according to filters
  - Parameters
    - amount
    - orderBy
    - location
    - status
    - length
    - themes
    -organization
    -openTo
    -search
    
  
- /hackathon/
  - Return info on a hackathon
  - Parameters
    -hackathonUrl
  
- /hackathon/submissions/
  - Return a list of all projects submitted to a hackathon
  - Parameters
    - hackathonUrl
    - category
    - sortBy
- /hackathon/categories/  
  - Return a list of all prize categories in a hackathon
  - Parameters
    - hackathonUrl
  
- /projects/
  - Return a list of most recent devpost projects
  - Parameters
    - amount
- /project/  
  - Return info on a project
  - Parameters
    - projectUrl
- /profile/projects/
  - Return a users projects
  - Parameters
    - username
- /profile/
  - Return info on a user
  - Parameters
    - username
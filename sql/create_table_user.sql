CREATE TABLE [user] (
  [userid] integer primary key autoincrement, 
  [username] CHAR, 
  [reg_time] DATE, 
  [password] CHAR, 
  [updatetime] CHAR, 
  [status] CHAR DEFAULT 0);
CREATE TABLE [tasks] (
  [taskid] INTEGER PRIMARY KEY AUTOINCREMENT, 
  [taskname] TEXT NOT NULL, 
  [taskdescr] TEXT NOT NULL, 
  [status] CHAR DEFAULT 0, 
  [createby] CHAR, 
  [createtime] DATETIME, 
  [updatetime] DATETIME);
import gzip
import os
import shutil

import utils


def handleCleanup(environ, start_response):
    c = utils.getCursor()
    # if you're a low admin
    if not utils.checkUserPermissions(environ['user'], 2):
        start_response("403 Permission Denied", [])
        return ["Access Denied"]

    for origin in ['main', 'missionMaker']:
        if origin == 'main':
            missionDirPrefix = utils.missionMainDir
            missionArchivePrefix = utils.missionMainArchive
            toBeArchivedProperty = 'toBeArchivedMain'
            toBeDeletedProperty = 'toBeDeletedMain'
            existsProperty = 'existsOnMain'
        else:
            missionDirPrefix = utils.missionMakerDir
            missionArchivePrefix = utils.missionMakerArchive
            toBeArchivedProperty = 'toBeArchivedMM'
            toBeDeletedProperty = 'toBeDeletedMM'
            existsProperty = 'existsOnMM'

        c.execute('''select * from versions where ''' + toBeArchivedProperty + ''' = 1''')
        toBeArchived = c.fetchall()

        for forArchival in toBeArchived:
            with open(missionDirPrefix + "/" + forArchival['name'], 'rb') as f_in:
                with gzip.open(os.path.join(missionArchivePrefix, forArchival['name'] + ".gz"), 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    os.remove(f_in.name)

        c.execute('''select * from versions where ''' + toBeDeletedProperty + ''' = 1''')
        toBeDeleted = c.fetchall()
        for deleteMe in toBeDeleted:
            try:
                os.remove(os.path.join(missionDirPrefix, deleteMe['name']))
            except OSError:
                pass
            
        c.execute(
            "update versions set " + existsProperty + " = 0, " + toBeArchivedProperty + " = 0, " + toBeDeletedProperty + " = 0 where " +
            toBeArchivedProperty + " = 1 or " + toBeDeletedProperty + " = 1")
    c.execute("delete from versions where existsOnMM = 0 and existsOnMain = 0")
    c.connection.commit()
    c.connection.close()

    start_response("200 OK", [])
    return []

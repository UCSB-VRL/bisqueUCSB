package bisque;
import java.io.DataOutputStream;
import java.io.FileInputStream;
import java.io.File;

public class FileProducer implements BQDataProducer {
    String filePath;

    public FileProducer  (String path) {
        filePath = path;
    }

    public String getName() {
        File file = new File(filePath);
        return file.getName();
    }

    public void convertToStream (DataOutputStream data){
        try{
            FileInputStream fileInputStream = new FileInputStream(filePath);
            int bytesAvailable = fileInputStream.available();
            int maxBufferSize = 1024;
            int bufferSize = Math.min(bytesAvailable, maxBufferSize);
            byte[] buffer = new byte[bufferSize];
            // read file and write it into form...
            int bytesRead = fileInputStream.read(buffer, 0, bufferSize);
            while (bytesRead > 0) {
                data.write(buffer, 0, bufferSize);
                bytesAvailable = fileInputStream.available();
                bufferSize = Math.min(bytesAvailable, maxBufferSize);
                bytesRead = fileInputStream.read(buffer, 0, bufferSize);
            }
            fileInputStream.close();
        }catch (Exception e){
            BQError.setLastError(e);
        }
    }
}
package bisque;

import java.io.DataOutputStream;

public interface BQDataProducer {

    String getName();
    void convertToStream (DataOutputStream os);

}


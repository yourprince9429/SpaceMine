class JSLoader {
    constructor() {
        this.loadedScripts = new Set();
    }

    async loadEncodedJS(filename) {
        if (this.loadedScripts.has(filename)) {
            return;
        }

        try {
            const response = await fetch(`/js/${filename}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            const base64Content = data.encoded_content;
            const binaryString = atob(base64Content);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            const decodedContent = new TextDecoder('utf-8').decode(bytes);
            
            const script = document.createElement('script');
            script.textContent = decodedContent;
            script.setAttribute('data-original-file', data.original_file);
            document.head.appendChild(script);
            
            this.loadedScripts.add(filename);
            
            return true;
        } catch (error) {
            
            try {
                const fallbackResponse = await fetch(`/js/raw/${filename}`);
                if (fallbackResponse.ok) {
                    const script = document.createElement('script');
                    script.src = `/static/js/${filename}`;
                    document.head.appendChild(script);
                    return true;
                }
            } catch (fallbackError) {
            }
            
            return false;
        }
    }

    async loadMultiple(filenames) {
        const promises = filenames.map(filename => this.loadEncodedJS(filename));
        const results = await Promise.allSettled(promises);
        
        const successful = results.filter(r => r.status === 'fulfilled' && r.value).length;
        const failed = results.length - successful;
        
        return { successful, failed };
    }
}

const jsLoader = new JSLoader();

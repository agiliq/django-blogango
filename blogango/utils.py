import logging                                                                                                                                                          

root_logger = logging.getLogger('')                                                                                                                                    
root_logger.setLevel(logging.DEBUG)
root_logger_stream = logging.StreamHandler()
root_logger_stream.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
root_logger.addHandler(root_logger_stream) 

